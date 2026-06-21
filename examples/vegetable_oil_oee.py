"""Real-world example: OEE of a vegetable-oil manufacturing plant.

Unlike the illustrative bottling-line example, every number here comes from a
peer-reviewed case study: the Overall Equipment Effectiveness factors measured
from a real vegetable-oil company's process data after a Total Productive
Maintenance (TPM) programme, together with the study's optimised targets.

    Tonny, F., Maliha, A., Chayan, M., & Xames, M. (2023). Optimization of
    overall equipment effectiveness (OEE) factors: Case study of a vegetable
    oil manufacturing company. Management Science Letters, 13(2), 124-135.
    https://doi.org/10.5267/j.msl.2022.12.002

The paper reports OEE as the three factors (availability, performance,
quality), not raw times and counts, so this example uses oee.oee_from_factors.
It shows a realistic point the textbook ~75% examples hide: a real plant can
have near-world-class quality while availability and performance hold OEE far
below the benchmark. Run:  python examples/vegetable_oil_oee.py
"""

import oee

# Reported means from the plant's process data, post-TPM (Tonny et al. 2023).
ACTUAL = dict(availability=0.6335, performance=0.6120, quality=0.96929)
# The paper's response-surface (central-composite) optimised targets.
TARGET = dict(availability=0.80103, performance=0.816022, quality=0.983052)


def main() -> None:
    print("== Vegetable-oil plant, measured OEE (Tonny et al. 2023) ==")
    r = oee.oee_from_factors(**ACTUAL, name="vegetable-oil plant (measured)")
    print(f"  availability {r.availability:.3f}  x  performance {r.performance:.3f}"
          f"  x  quality {r.quality:.3f}  =  OEE {r.oee:.4f}  ({r.oee:.1%})")
    print(f"  world-class (OEE >= 85%): {r.world_class}")

    factors = {"availability": r.availability,
               "performance": r.performance, "quality": r.quality}
    worst = min(factors, key=factors.get)
    print(f"  binding factor: {worst} ({factors[worst]:.1%}) - quality is already "
          f"near world-class; availability and performance are the drag\n")

    print("== The study's optimised targets (response-surface design) ==")
    t = oee.oee_from_factors(**TARGET, name="optimised target")
    print(f"  availability {t.availability:.3f}  x  performance {t.performance:.3f}"
          f"  x  quality {t.quality:.3f}  =  OEE {t.oee:.4f}  ({t.oee:.1%})")
    uplift = t.oee - r.oee
    print(f"  projected gain: +{uplift * 100:.1f} OEE points "
          f"({uplift / r.oee:.0%} relative), from availability and performance\n")

    print(r.summary())


if __name__ == "__main__":
    main()
