import json
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, Scale, Label, Entry, Button
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def get_project_data():
    try:
        with open('project_costs.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_project_data(data):
    with open('project_costs.json', 'w') as f:
        json.dump(data, f, indent=4)

def calculate_and_save_costs(api_fee, plan_hrs, impl_hrs, test_hrs, rate, infra_costs, maint_perc, overhead_perc):
    total_hours = plan_hrs + impl_hrs + test_hrs
    total_dev_cost = total_hours * rate
    maint_cost = (maint_perc / 100) * total_dev_cost
    overhead_cost = (overhead_perc / 100) * total_dev_cost
    initial_cost = total_dev_cost + overhead_cost + api_fee + infra_costs
    ongoing_costs = api_fee + infra_costs
    annual_maint_cost = maint_cost

    project_data = {
        "API Licensing Fee per Month": api_fee,
        "Total Development Hours": total_hours,
        "Total Development Cost": total_dev_cost,
        "Monthly Infrastructure Costs": infra_costs,
        "Annual Maintenance Cost": maint_cost,
        "Overhead Cost": overhead_cost,
        "Total Initial Cost": initial_cost,
        "Ongoing Monthly Costs": ongoing_costs,
        "Annual Maintenance Cost": annual_maint_cost
    }

    save_project_data(project_data)
    return project_data

def plot_comparison(project_data, third_party_costs):
    labels = ['In-House', 'Third-Party']
    values = [project_data['Total Initial Cost'] + sum([project_data['Ongoing Monthly Costs'] for _ in range(12)]), third_party_costs * 12]

    fig, ax = plt.subplots()
    ax.bar(labels, values, color=['blue', 'green'])
    ax.set_ylabel('Annual Costs ($)')
    ax.set_title('Cost Comparison: In-House vs. Third-Party')

    return fig

def gui_input():
    """
    Main function to run the GUI for inputting parameters and showing financial projections.
    """
    root = tk.Tk()
    root.title('Project Costs Management with Advanced Simulation Features')

    # Labels and entry widgets for user input
    third_party_label = Label(root, text="Enter third-party software's percentage of sales (%):")
    third_party_entry = Entry(root)
    sales_label = Label(root, text="Enter estimated annual sales through the application ($):")
    sales_entry = Entry(root)

    third_party_label.pack()
    third_party_entry.pack()
    sales_label.pack()
    sales_entry.pack()

    # Sliders for adjusting market growth and economic factors
    market_conditions_label = Label(root, text="Adjust market growth rate (%):")
    market_conditions_slider = Scale(root, from_=-100, to=100, orient='horizontal', label="Market Growth")
    economic_factors_slider = Scale(root, from_=-50, to=50, orient='horizontal', label="Economic Factors Adjustment")

    market_conditions_label.pack()
    market_conditions_slider.pack()
    economic_factors_slider.pack()

    # Button to calculate and show multi-year financial projections
    def calculate_multiyear_projections():
        # Fetch the project data by calculating costs again with current GUI inputs
        api_fee = float(simpledialog.askstring("API Fee", "Enter API licensing fee per month ($):", parent=root))
        plan_hrs = float(simpledialog.askstring("Planning Hours", "Enter hours for Planning and Analysis:", parent=root))
        impl_hrs = float(simpledialog.askstring("Implementation Hours", "Enter hours for Implementation:", parent=root))
        test_hrs = float(simpledialog.askstring("Testing Hours", "Enter hours for Testing and QA:", parent=root))
        rate = float(simpledialog.askstring("Hourly Rate", "Enter the hourly rate ($):", parent=root))
        infra_costs = float(simpledialog.askstring("Infrastructure Costs", "Enter monthly Infrastructure Costs ($):", parent=root))
        maint_perc = float(simpledialog.askstring("Maintenance Percentage", "Enter annual Maintenance Cost as a percentage of initial development cost (%):", parent=root))
        overhead_perc = float(simpledialog.askstring("Overhead Percentage", "Enter Overheads as a percentage of development cost (%):", parent=root))

        project_data = calculate_and_save_costs(api_fee, plan_hrs, impl_hrs, test_hrs, rate, infra_costs, maint_perc, overhead_perc)
        
        growth_rate = market_conditions_slider.get() + economic_factors_slider.get() / 100.0
        initial_sales = float(sales_entry.get())
        years = [initial_sales * ((1 + growth_rate / 100) ** year) for year in range(1, 6)]
        third_party_costs = [year * (float(third_party_entry.get()) / 100) for year in years]
        in_house_costs = [project_data['Total Initial Cost'] + project_data['Ongoing Monthly Costs'] * 12 for _ in years]

        fig, ax = plt.subplots()
        ax.plot(range(1, 6), in_house_costs, label='In-House Costs')
        ax.plot(range(1, 6), third_party_costs, label='Third-Party Costs')
        ax.set_xlabel('Years')
        ax.set_ylabel('Costs ($)')
        ax.set_title('5-Year Cost Projections with Sensitivity Analysis')
        ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    projection_button = Button(root, text="Calculate Multi-Year Projections", command=calculate_multiyear_projections)
    projection_button.pack()

    root.mainloop()

if __name__ == '__main__':
    gui_input()

