# spatial-decision-skills

> Patterns and examples for building AI-native spatial decision skills (not just API wrappers).

---

## 🧠 Why this repo exists

Many teams expose REST APIs directly as tools or MCP servers.

This often leads to:
- thin wrappers around endpoints
- low-level abstractions
- poor usability for AI agents

👉 This repo explores a different approach:

> **Skills as decision units, not API endpoints**

---

## 🎯 What are Spatial Decision Skills?

A Spatial Decision Skill:

- ✅ encapsulates a meaningful task  
- ✅ combines multiple operations  
- ✅ adds domain knowledge  
- ✅ returns usable results (often GeoJSON)

### ❌ API-style (what we avoid)
GET /places?lat=...&lon=...

### ✅ Skill-style (what we promote)
find-walkable-amenities  
score-location-potential  
analyze-geojson-area  

# Contributing
We welcome contributions from anyone and everyone. Please see our guidelines for contributing.

# License
This project is licensed under the Apache V2 License - see the LICENSE file for details.