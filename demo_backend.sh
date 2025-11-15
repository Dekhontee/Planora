#!/bin/bash

# demo_script.sh
# Demonstrates Planora backend API directly

echo "=== Planora Backend Demo ==="
echo ""
echo "Testing the /plan endpoint with sample Chemistry syllabus..."
echo ""

SYLLABUS="Chapter 1: Introduction to Chemistry
This chapter covers the fundamentals of chemistry, including the scientific method, states of matter, and basic atomic structure.

Chapter 2: Atomic Structure and Bonding
Explore the structure of atoms, electron configurations, and the periodic table.

Chapter 3: Stoichiometry and Reactions
Master the mole concept, chemical equations, and stoichiometric calculations.

Chapter 4: Thermodynamics and Kinetics
Understand energy changes in reactions (enthalpy), spontaneity (entropy), and reaction rates.

Chapter 5: Acid-Base Chemistry
Study pH, buffers, and neutralization reactions."

# Make the request
curl -s -X POST http://localhost:8000/plan \
  -F "syllabus_text=$SYLLABUS" \
  -F "exam_date=2025-12-20" \
  -F "hours_per_day=3.0" \
  -F "plan_length=14" \
  -F "course_type=Chemistry" | python3 -m json.tool | head -200

echo ""
echo "✅ Demo complete! Open Streamlit UI at http://localhost:8501 for the full experience."
