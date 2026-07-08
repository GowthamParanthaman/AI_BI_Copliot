from __future__ import annotations

from typing import Any

import pandas as pd

from loguru import logger


class RootCauseService:

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

    def analyze(
        self,
        df: pd.DataFrame,
        kpis: dict[str, Any],
        anomalies: list[dict[str, Any]]
    ) -> dict[str, Any]:

        logger.info(
            "Starting root cause analysis"
        )

        root_causes: list[
            dict[str, Any]
        ] = []

        financial = kpis.get(
            "financial",
            {}
        )

        operational = kpis.get(
            "operational",
            {}
        )

        category = kpis.get(
            "category",
            {}
        )

        # ==================================
        # REVENUE DRIVER
        # ==================================

        revenue = financial.get(
            "total_revenue",
            0
        )

        if revenue > 0:

            root_causes.append({

                "metric":
                    "Revenue",

                "cause":
                    "Revenue generation is the primary business driver",

                "impact":
                    self.HIGH,

                "confidence":
                    0.95,

                "evidence":
                    f"Total Revenue = {revenue}"
            })

        # ==================================
        # CUSTOMER DRIVER
        # ==================================

        revenue_per_customer = (
            financial.get(
                "revenue_per_customer",
                0
            )
        )

        if revenue_per_customer > 0:

            impact = (
                self.HIGH
                if revenue_per_customer > 1000
                else self.MEDIUM
            )

            root_causes.append({

                "metric":
                    "Customer Value",

                "cause":
                    "Customer purchasing behavior is influencing revenue",

                "impact":
                    impact,

                "confidence":
                    0.90,

                "evidence":
                    f"Revenue Per Customer = {revenue_per_customer}"
            })

        # ==================================
        # ORDER VOLUME
        # ==================================

        total_orders = (
            financial.get(
                "total_orders",
                0
            )
        )

        if total_orders > 0:

            root_causes.append({

                "metric":
                    "Orders",

                "cause":
                    "Order volume is contributing to overall performance",

                "impact":
                    self.HIGH,

                "confidence":
                    0.92,

                "evidence":
                    f"Total Orders = {total_orders}"
            })

        # ==================================
        # CATEGORY DRIVER
        # ==================================

        top_category = category.get(
            "top_category"
        )

        if top_category:

            root_causes.append({

                "metric":
                    "Category",

                "cause":
                    f"{top_category} contributes most to business activity",

                "impact":
                    self.MEDIUM,

                "confidence":
                    0.88,

                "evidence":
                    top_category
            })

        # ==================================
        # INVENTORY DRIVER
        # ==================================

        quantity = operational.get(
            "total_quantity",
            0
        )

        if quantity > 0:

            root_causes.append({

                "metric":
                    "Inventory",

                "cause":
                    "Product movement is influencing operational performance",

                "impact":
                    self.MEDIUM,

                "confidence":
                    0.85,

                "evidence":
                    f"Units Sold = {quantity}"
            })

        # ==================================
        # ANOMALY ROOT CAUSES
        # ==================================

        for anomaly in anomalies:

            severity = anomaly.get(
                "severity",
                self.LOW
            )

            confidence = {

                self.HIGH: 0.95,
                self.MEDIUM: 0.85,
                self.LOW: 0.75

            }.get(
                severity,
                0.70
            )

            root_causes.append({

                "metric":
                    anomaly.get(
                        "column",
                        "Unknown"
                    ),

                "cause":
                    "Abnormal data behavior detected",

                "impact":
                    severity,

                "confidence":
                    confidence,

                "evidence":
                    (
                        f"Anomalies = "
                        f"{anomaly.get('anomaly_count', 0)}"
                    )
            })

        # ==================================
        # RANK ROOT CAUSES
        # ==================================

        root_causes = sorted(

            root_causes,

            key=lambda x: (
                x["impact"] == self.HIGH,
                x["confidence"]
            ),

            reverse=True
        )

        result = {

            "root_causes":
                root_causes,

            "root_cause_count":
                len(root_causes),

            "top_root_cause":
                (
                    root_causes[0]
                    if root_causes
                    else None
                )
        }

        logger.success(
            f"Generated "
            f"{len(root_causes)} "
            f"root causes"
        )

        return result