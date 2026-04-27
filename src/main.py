from __future__ import annotations

import logging

try:
    from .recommender import (
        SocialRecommender,
        build_demo_report,
        default_data_dir,
        load_social_music_data,
        run_reliability_checks,
        summarize_user_analytics,
    )
except ImportError:
    from recommender import (
        SocialRecommender,
        build_demo_report,
        default_data_dir,
        load_social_music_data,
        run_reliability_checks,
        summarize_user_analytics,
    )


logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")


def main() -> None:
    data = load_social_music_data(default_data_dir())
    recommender = SocialRecommender(data)

    demo_users = ["u1", "u9"]
    for user_id in demo_users:
        recommendations = recommender.recommend_for_user(user_id, k=5)
        print("=" * 72)
        print(build_demo_report(user_id, data, recommendations))
        print()

        analytics = summarize_user_analytics(data, user_id)
        print(
            "Analytics: sent={sent_count}, successful={successful_count}, "
            "success_rate={success_rate}, best_context={best_context}".format(**analytics)
        )
        print()

    reliability = run_reliability_checks(data)
    print("=" * 72)
    print(f"Reliability checks passed: {reliability['passed']} / {reliability['total']}")
    for label, passed in reliability["checks"]:
        status = "PASS" if passed else "FAIL"
        print(f"- [{status}] {label}")


if __name__ == "__main__":
    main()
