from __future__ import annotations

from typing import Any

from loguru import logger

class AlertService:

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

    def generate_alerts(
        self,
        kpis: dict[str, Any],
        forecast_results: dict[str, Any],
        anomalies: list[dict[str, Any]],
        health_score: dict[str, Any]
    ) -> dict[str, Any]:

        logger.info(
            "Generating business alerts"
        )

        alerts = []

        executive_alerts = []

        operational_alerts = []

        financial = kpis.get(
            "financial",
            {}
        )

        growth_rate = float(
            forecast_results.get(
                "growth_rate",
                0
            )
        )

        revenue = float(
            financial.get(
                "total_revenue",
                0
            )
        )

        score = float(
            health_score.get(
                "business_health_score",
                100
            )
        )

        status = health_score.get(
            "status",
            "UNKNOWN"
        )

        high_anomalies = 0

        medium_anomalies = 0

        # ==================================
        # FORECAST ALERTS
        # ==================================

        if growth_rate < 0:

            alerts.append(

                self._create_alert(

                    severity=self.HIGH,

                    category="Forecast",

                    message=
                        "Revenue forecast is negative.",

                    action=
                        "Review sales strategy immediately.",

                    confidence=0.95
                )
            )

            executive_alerts.append(

                "Revenue decline forecasted."
            )

        elif growth_rate < 5:

            alerts.append(

                self._create_alert(

                    severity=self.MEDIUM,

                    category="Forecast",

                    message=
                        "Revenue growth forecast is weak.",

                    action=
                        "Evaluate growth initiatives.",

                    confidence=0.85
                )
            )

        # ==================================
        # ANOMALY ALERTS
        # ==================================

        for anomaly in anomalies:

            severity = anomaly.get(
                "severity",
                self.LOW
            )

            column = anomaly.get(
                "column",
                "Unknown"
            )

            if severity == self.HIGH:

                high_anomalies += 1

                alerts.append(

                    self._create_alert(

                        severity=self.HIGH,

                        category="Anomaly",

                        message=
                            f"High anomaly level detected in {column}.",

                        action=
                            "Investigate immediately.",

                        confidence=0.95
                    )
                )

            elif severity == self.MEDIUM:

                medium_anomalies += 1

                alerts.append(

                    self._create_alert(

                        severity=self.MEDIUM,

                        category="Anomaly",

                        message=
                            f"Moderate anomaly level detected in {column}.",

                        action=
                            "Monitor closely.",

                        confidence=0.85
                    )
                )

        # ==================================
        # REVENUE ALERTS
        # ==================================

        if revenue < 100000:

            alerts.append(

                self._create_alert(

                    severity=self.MEDIUM,

                    category="Revenue",

                    message=
                        "Revenue is below target threshold.",

                    action=
                        "Increase revenue generation activities.",

                    confidence=0.80
                )
            )

            operational_alerts.append(

                "Revenue below target threshold."
            )

        # ==================================
        # HEALTH SCORE ALERTS
        # ==================================

        if score < 40:

            alerts.append(

                self._create_alert(

                    severity=self.HIGH,

                    category="Business Health",

                    message=
                        f"Business health is CRITICAL ({score}).",

                    action=
                        "Executive intervention required.",

                    confidence=0.98
                )
            )

            executive_alerts.append(

                "Business health requires executive review."
            )

        elif score < 60:

            alerts.append(

                self._create_alert(

                    severity=self.MEDIUM,

                    category="Business Health",

                    message=
                        f"Business health is AT RISK ({score}).",

                    action=
                        "Review operational performance.",

                    confidence=0.90
                )
            )

        # ==================================
        # EXECUTIVE ALERTS
        # ==================================

        if high_anomalies > 0:

            executive_alerts.append(

                "Critical anomalies detected."
            )

        # ==================================
        # OPERATIONAL ALERTS
        # ==================================

        if medium_anomalies > 0:

            operational_alerts.append(

                "Monitor operational anomalies."
            )

        # ==================================
        # REMOVE DUPLICATES
        # ==================================

        alerts = list(

            {
                (
                    alert["category"],
                    alert["message"]
                ): alert

                for alert in alerts

            }.values()
        )

        # ==================================
        # PRIORITY SORTING
        # ==================================

        severity_rank = {

            self.HIGH: 3,
            self.MEDIUM: 2,
            self.LOW: 1
        }

        alerts = sorted(

            alerts,

            key=lambda alert:
                severity_rank.get(
                    alert["severity"],
                    0
                ),

            reverse=True
        )

        # ==================================
        # RESULT
        # ==================================

        result = {

            "alerts":
                alerts,

            "alert_count":
                len(alerts),

            "high_alerts":
                len([
                    a
                    for a in alerts
                    if a["severity"]
                    == self.HIGH
                ]),

            "medium_alerts":
                len([
                    a
                    for a in alerts
                    if a["severity"]
                    == self.MEDIUM
                ]),

            "executive_alerts":
                executive_alerts,

            "operational_alerts":
                operational_alerts,

            "business_status":
                status
        }

        logger.success(

            f"Generated "
            f"{len(alerts)} alerts"
        )

        return result

    # ==================================
    # ALERT FACTORY
    # ==================================

    def _create_alert(
        self,
        severity: str,
        category: str,
        message: str,
        action: str,
        confidence: float
    ) -> dict[str, Any]:

        return {

            "severity":
                severity,

            "category":
                category,

            "message":
                message,

            "action":
                action,

            "confidence":
                confidence,

            "generated_by":
                "AlertService"
        }