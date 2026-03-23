# Documentation

This directory contains all project documentation organized by category.

## Quick Navigation

- **[Player Guide](PLAYER_GUIDE.md)** - Complete user manual for playing the game
- **[Development Docs](development/)** - Guidelines and processes for contributors  
- **[Features](features/)** - Detailed feature implementation documentation
- **[Issues](issues/)** - Bug reports and issue tracking documentation
- **[Reports](reports/)** - Testing, security, and analysis reports
- **[Releases](releases/)** - Release notes and version summaries

## Directory Structure

```
docs/
├── PLAYER_GUIDE.md                    # Complete user manual
├── development/                       # Development documentation
│   ├── CODING_STANDARDS.md           # Code style and quality guidelines
│   ├── WORKFLOW.md                   # Development workflow and processes  
│   └── ENHANCEMENTS.md               # Future enhancement proposals
├── features/                         # Feature documentation
│   ├── FEATURE_CANONICAL_NPCS.md    # Canonical NPCs implementation plan
│   ├── FEATURE_DOCUMENTATION_COMPLETION.md # Documentation completion feature
│   ├── FEATURE_SECURITY_VALIDATION.md # Security validation feature
│   └── DESIGN_NPC_CONVERSATIONS.md  # NPC conversation system design
├── issues/                           # Bug reports and issue tracking
│   ├── README.md                     # Issue tracking guidelines
│   ├── active/                       # Open/unresolved issues
│   │   └── BUG_EGG_OPENABLE_TOO_EARLY.md
│   ├── resolved/                     # Fixed/closed issues
│   │   └── BUG_REPORT_Navigation.md
│   └── templates/                    # Issue report templates
│       ├── bug-report-template.md
│       └── feature-request-template.md
├── reports/                          # Analysis and testing reports
│   ├── COMMAND_TESTING_REPORT.md    # Command validation report
│   ├── NPC_STATUS_REPORT.md         # NPC implementation status
│   ├── PHASE_2_COMPLETION_REPORT.md # Thief NPC completion report
│   └── SECURITY_REPORT.md           # Security analysis report
└── releases/                         # Release documentation  
    ├── RELEASE_NOTES_v1.0.0.md      # v1.0.0 release notes
    ├── RELEASE_NOTES_v1.2.2.md      # v1.2.2 release notes
    └── v1.2.2_RELEASE_SUMMARY.md    # v1.2.2 summary
```

## Essential Documents

For new users and contributors, start with:

1. **[../README.md](../README.md)** - Project overview and quick start
2. **[PLAYER_GUIDE.md](PLAYER_GUIDE.md)** - Complete gameplay instructions  
3. **[development/CODING_STANDARDS.md](development/CODING_STANDARDS.md)** - Development guidelines
4. **[issues/README.md](issues/README.md)** - Bug reporting and issue tracking
5. **[features/FEATURE_CANONICAL_NPCS.md](features/FEATURE_CANONICAL_NPCS.md)** - Current major feature in progress

## Contributing

All documentation should follow markdown best practices and maintain internal consistency. When adding new documentation:

- Place user-facing docs in `docs/` root
- Place development docs in `docs/development/`  
- Place feature specifications in `docs/features/`
- Place bug reports and issues in `docs/issues/active/` (move to `resolved/` when fixed)
- Place analysis reports in `docs/reports/`
- Place release documentation in `docs/releases/`

Update this README.md when adding new major documentation files.