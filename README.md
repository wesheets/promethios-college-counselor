# Promethios College Counselor

A standalone, separately branded education vertical built on the Promethios core architecture. This demo implements an emotion-aware college counseling system with transparent trust scores and comprehensive reporting.

## Architecture Goals

1. **Vertical Isolation**: Create a standalone, separately branded education vertical
2. **Emotion-Aware Counseling**: Implement journaling with emotional state monitoring
3. **Trust-Based Recommendations**: Provide college recommendations with transparent trust scores
4. **Override System**: Allow counselors or students to override recommendations with justification
5. **Comprehensive Reporting**: Generate detailed reports with full decision trails

## Repository Structure

```
promethios-college-counselor/
├── api/
│   ├── .env.example
│   ├── Procfile
│   ├── requirements.txt
│   ├── runtime.txt
│   ├── college_counselor_api/
│   │   ├── app.py
│   │   ├── counseling_wrapper.py
│   │   └── college_data_loader.py
│   └── promethios_core/
│       ├── governance_core.py
│       ├── hash_chain.py
│       └── schema_validation.py
├── web/
│   ├── .env.example
│   ├── Procfile
│   ├── app.py
│   ├── requirements.txt
│   └── templates/
│       ├── index.html
│       ├── profile.html
│       ├── journal.html
│       ├── colleges.html
│       ├── report.html
│       └── settings.html
└── render.yaml
```

## Features

- Multi-factor trust evaluation framework for education-specific factors
- Conversational AI for student goals and anxieties
- College data integration with transparent recommendations
- Comprehensive reporting with full decision trails
- Override system with justification requirements

## Development

This project is currently under development. More details will be added as implementation progresses.
