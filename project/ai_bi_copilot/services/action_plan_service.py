from typing import Any

from loguru import logger


class ActionPlanService:

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

    def generate_action_plan(
        self,
        recommendations: dict[str, Any],
        alerts: dict[str, Any],
        health_score: dict[str, Any]
    ) -> dict[str, Any]:

        logger.info(
            "Generating enterprise action plan"
        )

        actions = []

        # ==================================
        # HIGH PRIORITY RECOMMENDATIONS
        # ==================================

        for item in recommendations.get(
            "high_priority",
            []
        ):

            actions.append(

                self._create_action(

                    action=item.get(
                        "recommendation"
                    ),

                    owner="Executive Team",

                    timeline=item.get(
                        "timeline",
                        "30 days"
                    ),

                    impact=item.get(
                        "impact",
                        "HIGH"
                    ),

                    risk_level=self.HIGH,

                    source="Recommendation Engine"
                )
            )

        # ==================================
        # MEDIUM PRIORITY RECOMMENDATIONS
        # ==================================

        for item in recommendations.get(
            "medium_priority",
            []
        ):

            actions.append(

                self._create_action(

                    action=item.get(
                        "recommendation"
                    ),

                    owner="Operations Team",

                    timeline=item.get(
                        "timeline",
                        "60 days"
                    ),

                    impact=item.get(
                        "impact",
                        "MEDIUM"
                    ),

                    risk_level=self.MEDIUM,

                    source="Recommendation Engine"
                )
            )

        # ==================================
        # ALERT DRIVEN ACTIONS
        # ==================================

        for alert in alerts.get(
            "alerts",
            []
        ):

            severity = alert.get(
                "severity",
                self.LOW
            )

            if severity in [
                self.HIGH,
                self.MEDIUM
            ]:

                actions.append(

                    self._create_action(

                        action=alert.get(
                            "action"
                        ),

                        owner="Risk Management",

                        timeline="Immediate",

                        impact="Risk Reduction",

                        risk_level=severity,

                        source="Alert Engine"
                    )
                )

        # ==================================
        # HEALTH SCORE ACTIONS
        # ==================================

        score = health_score.get(
            "business_health_score",
            100
        )

        if score < 40:

            actions.append(

                self._create_action(

                    action=
                    "Perform full business review",

                    owner=
                    "Executive Leadership",

                    timeline=
                    "7 days",

                    impact=
                    "Business Recovery",

                    risk_level=
                    self.HIGH,

                    source=
                    "Health Score Engine"
                )
            )

        elif score < 60:

            actions.append(

                self._create_action(

                    action=
                    "Review operational performance",

                    owner=
                    "Operations Team",

                    timeline=
                    "30 days",

                    impact=
                    "Operational Improvement",

                    risk_level=
                    self.MEDIUM,

                    source=
                    "Health Score Engine"
                )
            )

        # ==================================
        # REMOVE DUPLICATES
        # ==================================

        actions = list(

            {
                action["action"]: action

                for action in actions

            }.values()
        )

        # ==================================
        # SORT BY RISK
        # ==================================

        risk_rank = {

            self.HIGH: 3,
            self.MEDIUM: 2,
            self.LOW: 1
        }

        actions = sorted(

            actions,

            key=lambda x:

                risk_rank.get(
                    x["risk_level"],
                    0
                ),

            reverse=True
        )

        # ==================================
        # ASSIGN PRIORITY
        # ==================================

        for index, action in enumerate(
            actions,
            start=1
        ):

            action["priority"] = index

        executive_roadmap = [

            action["action"]

            for action

            in actions[:5]
        ]

        result = {

            "action_plan":
                actions,

            "action_count":
                len(actions),

            "executive_roadmap":
                executive_roadmap,

            "high_priority_actions":
                len([
                    a
                    for a in actions
                    if a["risk_level"]
                    == self.HIGH
                ]),

            "medium_priority_actions":
                len([
                    a
                    for a in actions
                    if a["risk_level"]
                    == self.MEDIUM
                ])
        }

        logger.success(

            f"Generated "
            f"{len(actions)} "
            f"action plans"
        )

        return result

    # ==================================
    # ACTION FACTORY
    # ==================================

    def _create_action(
        self,
        action: str,
        owner: str,
        timeline: str,
        impact: str,
        risk_level: str,
        source: str
    ) -> dict[str, Any]:

        return {

            "action":
                action,

            "owner":
                owner,

            "timeline":
                timeline,

            "expected_impact":
                impact,

            "risk_level":
                risk_level,

            "source":
                source
        }