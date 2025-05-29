from collections import defaultdict
from pathlib import Path
from containment.mcp.clients.basic import MCPClient

# from containment.mcp.clients.experts.proof import SORRY_CANARY
from containment.structures import (
    HoareTriple,
    Polarity,
    ExpertMetadata,
    VerificationFailure,
    VerificationResult,
)
from pantograph.search import Agent
from pantograph.expr import GoalState, Tactic


class HoareSearch(Agent):
    """Search agent (dumb) for Hoare triple proofs."""

    def __init__(self) -> None:
        super().__init__()
        self.goal_tactic_id_map = defaultdict(lambda: defaultdict(int))
        self.constant_tactics = [
            "simp",
            "simp [Expr.eval]",
            "simp [Env.set]",
            "simp [Env.get]",
            "aesop",
            "intros",
            "assumption",
            "apply hoare_skip",
            "apply hoare_seq",
            "apply hoare_assign",
            "apply hoare_if",
            "apply hoare_while",
            "constructor",
            "omega",
            "rw [Value.int_lt]",
            "simp [Value.int_lt]",
        ]
        self.tactic_templates = {"cases": "cases {h}", "intros1": "intros {h1}"}

    @property
    def tactics(self) -> list[str]:
        return self.constant_tactics

    def next_tactic(self, state: GoalState, goal_id: int) -> Tactic | None:
        key = state.state_id
        idx = self.goal_tactic_id_map[key][goal_id]
        # target = state.goals[goal_id].target
        tactics = self.tactics
        variables = state.goals[goal_id].variables
        for variable in variables:
            tactics.append(self.tactic_templates["cases"].format(h=variable))
        if idx > len(tactics):
            return None
        self.goal_tactic_id_map[key][goal_id] += 1
        return tactics[idx]

    def reset(self) -> None:
        """
        Called after search
        """
        self.__init__()


class Expert(MCPClient):
    """Expert at writing hoare proofs over imp, via minimal search."""

    def __init__(self, triple: HoareTriple, polarity: Polarity) -> None:
        super().__init__()
        self.triple = triple
        self.polarity = polarity
        self.verification_result = None
        self.search_agent = HoareSearch()

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
