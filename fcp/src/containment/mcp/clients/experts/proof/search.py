from collections import defaultdict
from itertools import chain
from pathlib import Path
from containment.mcp.clients.basic import MCPClient
from containment.structures import (
    HoareTriple,
    Polarity,
    ExpertMetadata,
    VerificationFailure,
    VerificationResult,
)
from containment.fsio.prompts import load_txt
from containment.fsio.tools import pantograph_init, temp_lakeproj_init
from pantograph.search import Agent
from pantograph.expr import GoalState, Tactic


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


class HoareSearch(Agent):
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

    def __init__(self, triple: HoareTriple, polarity: Polarity) -> None:
        super().__init__()
        self.triple = triple
        self.polarity = polarity
        self.verification_result = None
        self.search_agent = HoareSearch()
        self.lean_file_sorry = load_txt(
            f"{polarity.value}.lean.template", proof="sorry", **triple.model_dump()
        )
        self.cwd = temp_lakeproj_init()
        self.pantograph_server = pantograph_init(self.cwd)

    @classmethod
    async def connect_and_run(cls, triple: HoareTriple, polarity: Polarity) -> "Expert":
        mcp_client = cls(triple, polarity)
        mcp_client.verification_result = await mcp_client._connect_to_server_and_run()
        return mcp_client

    async def run(self) -> VerificationResult:
        """Run the functionality of the client."""
        return [
            VerificationFailure(
                triple=self.triple,
                proof="TODO: not implemented",
                audit_trail=Path("."),
                error_message="TODO: not implemented.",
                metadata=ExpertMetadata(model="no model?", polarity=Polarity.POS),
            )
        ]
