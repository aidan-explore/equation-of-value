import matplotlib.pyplot as plt
import seaborn as sns
from models.healthpost import HealthPost

def chart_cost_breakdown(hp: HealthPost) -> plt:

    # Create a bar chart to show each of the individual costs in the total cost
    plt.figure(figsize=(10, 6))
    sns.barplot(x=["Salaries", "Cost of Care", "Equipment Capital", "Equipment Maintenance"], 
                y=[hp.salaries_cost, hp.cost_of_care, hp.equipment_capital, hp.equipment_maintenance], palette="husl")

    # Set title and labels
    plt.title("Individual Costs in Total Cost")
    plt.xlabel("Cost Category")
    plt.ylabel("Cost (USD)")

    return plt