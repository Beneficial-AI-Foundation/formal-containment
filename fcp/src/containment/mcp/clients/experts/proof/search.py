from collections import defaultdict
from itertools import chain
from pathlib import Path
from containment.mcp.clients.basic import MCPClient
from containment.fsio.logs import logs
from containment.structures import (
    HoareTriple,
    Polarity,
    ExpertMetadata,
    VerificationFailure,
    VerificationSuccess,
    VerificationResult,
)
from containment.fsio.prompts import load_txt
from containment.fsio.tools import pantograph_init, temp_lakeproj_init
from containment.fsio.artifacts import write_artifact
from pantograph.expr import GoalState, Tactic
from pantograph.search import Agent
from pantograph.server import Server


DEFS = ["Expr.eval", "Env.set", "Env.get"]
HOARE_THMS = [
    "hoare_skip",
    "hoare_seq",
    "hoare_assign",
    "hoare_if",
    "hoare_while",
    "hoare_consequence_pre",
    "hoare_consequence_post",
    "hoare_consequence",
]
THMS = ["Value.int_lt"]
CONSTANTS = ["simp", "aesop", "assumption", "constructor", "omega"]
TACTIC_FNS = {
    "simp": "simp [{defn}]",
    "rw": "rw [{equ}]",
    "cases": "cases {hyp}",
    "intros": "intros {hyp}",
    "apply": "apply {hyp}",
}


class DumbHoareSearch(Agent):
    """Search agent (dumb) for Hoare triple proofs."""

    def __init__(self) -> None:
        super().__init__()
        self.goal_tactic_id_map = defaultdict(lambda: defaultdict(int))
        self.tactics_base = list(
            chain(
                CONSTANTS,
                [TACTIC_FNS["simp"].format(defn=defn) for defn in DEFS],
                [TACTIC_FNS["rw"].format(equ=equ) for equ in THMS],
                [TACTIC_FNS["apply"].format(hyp=hyp) for hyp in HOARE_THMS],
            )
        )

    def next_tactic(self, state: GoalState, goal_id: int) -> Tactic | None:
        key = state.state_id
        idx = self.goal_tactic_id_map[key][goal_id]
        # target = state.goals[goal_id].target
        tactics = self.tactics_base.copy()
        variables = state.goals[goal_id].variables
        for variable in variables:
            tactics.append(TACTIC_FNS["cases"].format(hyp=variable))
        if idx >= len(tactics):
            return None
        self.goal_tactic_id_map[key][goal_id] += 1
        return tactics[idx]

    def reset(self) -> None:
        """
        Called after search
        """
        self.goal_tactic_id_map.clear()


class Expert(MCPClient):
    """Expert at writing hoare proofs over imp, via minimal search."""

    def __init__(
        self,
        model: str,
        triple: HoareTriple,
        polarity: Polarity,
        *,
        max_steps: int,
        max_trials_per_goal: int,
        pantog_verbose: bool,
    ) -> None:
        super().__init__()
        self.model = model
        self.triple = triple
        self.polarity = polarity
        self.max_steps = max_steps
        self.max_trials_per_goal = max_trials_per_goal
        self.pantog_verbose = pantog_verbose
        self.code_dt = []
        self.verification_result = None
        self.search_agent = DumbHoareSearch()
        self.lean_file_sorry = self._render_code(None)
        self.cwd = temp_lakeproj_init()
        self.pantograph_server: Server | None = None

    def _render_code(self, proof: str | None) -> str:
        """
        Write the proof to a file in the tmpdir.
        """
        basic = load_txt(
            f"search/{self.polarity.value}.lean.template",
            proof=proof if proof is not None else "sorry",
            **self.triple.model_dump(),
        )
        self.code_dt.append(basic)
        return basic

    @classmethod
    async def connect_and_run(
        cls,
        model: str,
        triple: HoareTriple,
        polarity: Polarity,
        *,
        max_steps: int,
        max_trials_per_goal: int,
        pantog_verbose: bool = False,
    ) -> "Expert":
        mcp_client = cls(
            model,
            triple,
            polarity,
            max_steps=max_steps,
            max_trials_per_goal=max_trials_per_goal,
            pantog_verbose=pantog_verbose,
        )
        mcp_client.pantograph_server = await pantograph_init(mcp_client.cwd)
        mcp_client.verification_result = await mcp_client._connect_to_server_and_run()
        return mcp_client

    async def _proof_search(self) -> VerificationResult:
        """
        Perform the proof search using the HoareSearch agent.
        """
        failures = []
        if self.pantograph_server is None:
            failures.append(
                VerificationFailure(
                    triple=self.triple,
                    proof="",
                    error_message="Pantograph server is not initialized.",
                    audit_trail=Path.cwd(),
                    metadata=ExpertMetadata(
                        model=self.model,
                        polarity=self.polarity,
                        iteration=0,
                        success=False,
                    ),
                )
            )
            return failures
        logs.info(f"{self.model}: Lean file with sorry: {self.lean_file_sorry}")
        units = await self.pantograph_server.load_sorry_async(self.lean_file_sorry)
        logs.info(f"{self.model}: pantograph loaded the following sorry units: {units}")
        tactics = "sorry"
        for unit in units:
            if unit.goal_state is None:
                failures.append(
                    VerificationFailure(
                        triple=self.triple,
                        proof="",
                        error_message="||".join(unit.messages),
                        audit_trail=Path.cwd(),
                        metadata=ExpertMetadata(
                            model=self.model,
                            polarity=self.polarity,
                            iteration=0,
                            success=False,
                        ),
                    )
                )
                return failures
            search_result = self.search_agent.search(
                self.pantograph_server,
                unit.goal_state,
                max_steps=self.max_steps,
                max_trials_per_goal=self.max_trials_per_goal,
                verbose=self.pantog_verbose,
            )
            tactics = self.search_agent.tactics_base[
                self.search_agent.goal_tactic_id_map[unit.goal_state.state_id][0]
            ]
            lean_file_next = self.lean_file_sorry.replace(
                "sorry",
                f"{tactics}",
            )
            self.code_dt.append(lean_file_next)
            artifact_dir = write_artifact(self.cwd, self.code_dt[0])
            if search_result.success:
                return VerificationSuccess(
                    triple=self.triple,
                    audit_trail=artifact_dir / f"{hash(self.triple)}.lean",
                    proof=tactics,
                    metadata=ExpertMetadata(
                        model=self.model,
                        polarity=self.polarity,
                        iteration=search_result.steps,
                        success=True,
                    ),
                )
            else:
                failures.append(
                    VerificationFailure(
                        triple=self.triple,
                        proof=tactics,
                        error_message="Proof search failed",
                        audit_trail=Path.cwd(),
                        metadata=ExpertMetadata(
                            model=self.model,
                            polarity=self.polarity,
                            iteration=0,
                            success=False,
                        ),
                    )
                )
        return failures

    async def run(self) -> VerificationResult:
        """Run the functionality of the client."""
        return await self._proof_search()
