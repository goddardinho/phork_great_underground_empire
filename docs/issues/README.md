# Issues Documentation

This directory contains bug reports, issue tracking, and related documentation for the project.

## Directory Structure

- **[active/](active/)** - Currently open/unresolved issues and bug reports
- **[resolved/](resolved/)** - Fixed/closed issues (kept for reference and context)
- **[templates/](templates/)** - Issue report templates for consistent documentation

## Issue Lifecycle

### Reporting a New Issue
1. Use the [bug report template](templates/bug-report-template.md) to create a new issue
2. Place the new issue file in `active/` directory
3. Use descriptive filename: `BUG_COMPONENT_DESCRIPTION.md`

### Resolving an Issue  
1. Update the issue file with resolution details
2. Move from `active/` to `resolved/` directory
3. Update any related documentation or changelog entries

## Current Issues

### Active Issues
<!-- Update this section when adding/removing active issues -->
- [BUG_EGG_OPENABLE_TOO_EARLY.md](active/BUG_EGG_OPENABLE_TOO_EARLY.md) - Jewel-encrusted egg opens before intended game progression

### Recently Resolved
- [BUG_REPORT_Navigation.md](resolved/BUG_REPORT_Navigation.md) - Room navigation mapping issue (Fixed: March 2026)

## Guidelines

### Bug Report Standards
- **Clear titles**: Use component and brief description
- **Reproducible steps**: Detailed steps to reproduce the issue
- **Expected vs actual behavior**: What should happen vs what actually happens  
- **Impact assessment**: How the bug affects gameplay or system functionality
- **Suggested fixes**: Initial thoughts on potential solutions (if applicable)

### File Naming Convention
```
BUG_[COMPONENT]_[BRIEF_DESCRIPTION].md

Examples:
- BUG_NAVIGATION_ROOM_CONNECTIVITY.md
- BUG_INVENTORY_ITEM_DUPLICATION.md  
- BUG_PARSER_COMMAND_AMBIGUITY.md
- BUG_NPC_BEHAVIOR_THIEF_INTERACTION.md
```

## Integration with Development

- Issues should reference relevant test files in `/tests`
- Fixed issues should be documented in `CHANGELOG.md`
- Consider adding tests to prevent regression of resolved issues
- Link to actual commits that resolve issues when possible

## See Also

- [../development/CODING_STANDARDS.md](../development/CODING_STANDARDS.md) - Code quality guidelines
- [../../tests/README.md](../../tests/README.md) - Testing documentation  
- [../../CHANGELOG.md](../../CHANGELOG.md) - Change history and resolved issues