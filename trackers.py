from collections import defaultdict
from tabulate import tabulate

SON_EMOJIS = {
    "wise_son": "🧠",
    "wicked_son": "😈",
    "simple_son": "🙂",
    "son_who_does_not_know_to_ask": "🤷"
}
class DiagnosisTracker:

    def __init__(self, sons_descriptions: dict):
        self.sons = sons_descriptions.keys()
        self.evaluations_by_round = []

    def add_round_data(self, round_data: dict):
        """
        Expects a dictionary of the form:
        {
            "wise_son": {"likelihood": 0.7, "explanation": "..."},
            ...
        }
        """
        self.evaluations_by_round.append(round_data)

    def compute_averages(self):
        """
        Returns a dictionary:
        {
            "wise_son": 0.72,
            "wicked_son": 0.12,
            ...
        }
        """
        final_distribution = {}
        for son in self.sons:
            total = sum(round_data[son]["likelihood"] for round_data in self.evaluations_by_round)
            avg = total / len(self.evaluations_by_round)
            final_distribution[son] = avg
        return final_distribution

    def print_summary(self):
        final_distribution = self.compute_averages()
        total = sum(final_distribution.values())

        # Compute percentages
        percentage_distribution = {
            son: (score / total) * 100 for son, score in final_distribution.items()
        }

        # Add emoji and sort by percentage descending
        sorted_distribution = sorted(
            percentage_distribution.items(), key=lambda x: x[1], reverse=True
        )
        table_data = [
            [f"{SON_EMOJIS.get(son, '')} {son}", f"{score:.1f}%"]
            for son, score in sorted_distribution
        ]

        print("\n📊 Final Diagnosis (by Percentage):")
        print(tabulate(
            table_data,
            headers=["Son", "Likelihood"],
            tablefmt="grid"
        ))

        most_likely, score = sorted_distribution[0]
        print(f"\n🌟 Most likely son type: {SON_EMOJIS.get(most_likely, '')} {most_likely} ({score:.1f}%)")