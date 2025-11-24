import streamlit as st
from research import search_company, get_latest_news, get_wikipedia_summary, get_financials
from generator import synthesize_research, generate_account_plan
from memory import save_plan, load_plan, list_saved_companies, update_plan_section
import os

def plan_dict_to_text(plan_dict):
    """Convert plan dictionary into a clean markdown string."""
    lines = []
    for section, content in plan_dict.items():
        lines.append(f"### {section}\n{content}\n")
    return "\n".join(lines)

st.set_page_config(page_title="Company Research Assistant", layout="wide")

st.title("Company Research Assistant")

# Sidebar: saved plans
st.sidebar.header("Saved Account Plans")
companies = list_saved_companies()
selected_saved = st.sidebar.selectbox("Open saved plan", ["-- New --"] + companies)

if selected_saved and selected_saved != "-- New --":
    plan = load_plan(selected_saved)
    st.sidebar.success(f"Loaded: {selected_saved}")

# Main UI
col1, col2 = st.columns([3, 1])

with col1:
    company_name = st.text_input("Company name (e.g. Tesla, Inc.)")
    #company_ticker = st.text_input("Ticker (optional, for yfinance) e.g. TSLA")

    if st.button("Generate Account Plan"):
        if not company_name:
            st.error("Please enter a company name.")
        else:
            with st.spinner("Gathering research: web, news, wikipedia, financials..."):
                web_results = search_company(company_name)
                news = get_latest_news(company_name)
                wiki = get_wikipedia_summary(company_name)
                financials = None

            st.info("Synthesizing research with LLM (Gemini)...")
            summary, conflicts = synthesize_research(
                company_name, web_results, news, wiki
            )

            st.markdown("### Synthesized Summary")
            st.write(summary)

            if conflicts:
                st.warning("Conflicts detected in the sources:")
                for c in conflicts:
                    st.write("- ", c)

            st.info("Generating Account Plan...")
            plan = generate_account_plan(company_name, summary)

            st.markdown("### Account Plan")
            if isinstance(plan, dict):
                plan_text = plan_dict_to_text(plan)
            else:
                plan_text = plan

            st.markdown(plan_text)

            save_plan(company_name, plan)
            st.success("Plan saved. Use the sidebar to open saved plans.")

with col2:
    st.header("Edit saved plan")
    edit_company = st.text_input("Company to edit (exact name)")
    edit_section = st.text_input("Section title to replace (exact heading)")
    new_text = st.text_area("New content for the section")
    if st.button("Update Section"):
        if not (edit_company and edit_section and new_text):
            st.error("Fill all fields to update a section.")
        else:
            updated = update_plan_section(edit_company, edit_section, new_text)
            if updated:
                st.success("Section updated and saved.")
            else:
                st.error("Update failed — check company name and section heading.")

# Footer: sample output
st.markdown("---")