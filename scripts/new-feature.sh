#!/bin/bash
# New Feature Branch Helper Script
# Creates a new feature branch with documentation reminders and tagging preparation

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Creating New Feature Branch${NC}"
echo "=================================="

# Get branch name from user
if [ -z "$1" ]; then
    echo -e "${YELLOW}Usage: ./scripts/new-feature.sh <feature-name>${NC}"
    echo -e "${YELLOW}Example: ./scripts/new-feature.sh security-validation${NC}"
    exit 1
fi

FEATURE_NAME=$1
BRANCH_NAME="feature/$FEATURE_NAME"

# Check if we're on main/master
current_branch=$(git rev-parse --abbrev-ref HEAD)
if [[ "$current_branch" != "main" ]] && [[ "$current_branch" != "master" ]]; then
    echo -e "${RED}❌ Please switch to main branch first${NC}"
    echo -e "${YELLOW}Run: git checkout main${NC}"
    exit 1
fi

# Pull latest changes
echo -e "${BLUE}📥 Pulling latest changes...${NC}"
git pull origin $current_branch

# Create and switch to new branch
echo -e "${BLUE}🌿 Creating branch: $BRANCH_NAME${NC}"
git checkout -b "$BRANCH_NAME"

# Get current version info
latest_tag=$(git describe --tags --abbrev=0 2>/dev/null || echo "v1.0.0")
current_version=$(echo $latest_tag | sed 's/v//')
next_patch=$(echo $current_version | awk -F. -v OFS=. '{$NF = $NF + 1; print}')
next_minor=$(echo $current_version | awk -F. -v OFS=. '{$(NF-1) = $(NF-1) + 1; $NF = 0; print}')

echo ""
echo -e "${GREEN}📋 Feature Branch Setup Complete!${NC}"
echo -e "${GREEN}Branch: $BRANCH_NAME${NC}"
echo -e "${GREEN}Latest tag: $latest_tag${NC}"
echo ""

# Create a feature planning template
FEATURE_PLAN="FEATURE_${FEATURE_NAME^^}.md"
cat > "$FEATURE_PLAN" << EOF
# Feature: $FEATURE_NAME

## Overview
Brief description of what this feature accomplishes.

## Tasks
- [ ] Task 1
- [ ] Task 2  
- [ ] Update documentation
- [ ] Add/update tests
- [ ] Update CHANGELOG.md
- [ ] Create git tag when complete

## Documentation Updates Needed
- [ ] TODO.md - Mark items complete or add new ones
- [ ] CHANGELOG.md - Add entry for this feature
- [ ] README.md - Update if public-facing changes
- [ ] Other: _______________

## Suggested Version Bump
- Patch (bug fixes, small improvements): v$next_patch
- Minor (new features, enhancements): v$next_minor  
- Major (breaking changes): $(echo $current_version | awk -F. -v OFS=. '{$1 = $1 + 1; $2 = 0; $3 = 0; print}')

## Ready to Push Checklist
- [ ] All tasks completed
- [ ] Tests passing  
- [ ] Documentation updated
- [ ] CHANGELOG.md entry added
- [ ] Version tag created
- [ ] Pre-push hook validates successfully

EOF

echo -e "${YELLOW}📄 Created feature plan: $FEATURE_PLAN${NC}"
echo -e "${YELLOW}💡 Edit this file to track your progress${NC}"
echo ""
echo -e "${GREEN}🎯 Next Steps:${NC}"
echo "1. Work on your feature"
echo "2. Update documentation as you go"
echo "3. When ready to push, the pre-push hook will check your documentation"
echo "4. Create a version tag when the feature is complete:"
echo -e "   ${BLUE}git tag -a v$next_patch -m \"Feature: $FEATURE_NAME\"${NC}"
echo "5. Push with: ${BLUE}git push origin $BRANCH_NAME${NC}"
echo ""
echo -e "${GREEN}Happy coding! 🎮✨${NC}"