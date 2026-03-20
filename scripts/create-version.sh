#!/bin/bash
# Version Management Script
# Helps create version tags and update documentation

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🏷️  Version Management${NC}"
echo "======================"

# Get current version info
latest_tag=$(git describe --tags --abbrev=0 2>/dev/null || echo "v1.0.0")
current_version=$(echo $latest_tag | sed 's/v//')
current_branch=$(git rev-parse --abbrev-ref HEAD)

echo -e "${BLUE}Current branch: $current_branch${NC}"
echo -e "${BLUE}Latest tag: $latest_tag${NC}"

# Check if there are commits since last tag
commits_since_tag=$(git rev-list --count $latest_tag..HEAD 2>/dev/null || echo "0")
echo -e "${BLUE}Commits since last tag: $commits_since_tag${NC}"

if [[ "$commits_since_tag" == "0" ]]; then
    echo -e "${YELLOW}💡 No new commits since last tag${NC}"
    exit 0
fi

# Suggest version numbers
patch_version="v$(echo $current_version | awk -F. -v OFS=. '{$NF = $NF + 1; print}')"
minor_version="v$(echo $current_version | awk -F. -v OFS=. '{$(NF-1) = $(NF-1) + 1; $NF = 0; print}')"
major_version="v$(echo $current_version | awk -F. -v OFS=. '{$1 = $1 + 1; $2 = 0; $3 = 0; print}')"

echo ""
echo -e "${GREEN}📊 Version Options:${NC}"
echo "1. Patch ($patch_version) - Bug fixes, small improvements"
echo "2. Minor ($minor_version) - New features, enhancements"  
echo "3. Major ($major_version) - Breaking changes"
echo "4. Custom version"
echo "5. Exit without creating tag"

echo ""
read -p "Choose version type (1-5): " choice

case $choice in
    1)
        new_version=$patch_version
        ;;
    2)
        new_version=$minor_version
        ;;
    3)
        new_version=$major_version
        ;;
    4)
        read -p "Enter custom version (e.g., v1.4.2): " custom_version
        if [[ $custom_version =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
            new_version=$custom_version
        else
            echo -e "${RED}❌ Invalid version format. Use vX.Y.Z${NC}"
            exit 1
        fi
        ;;
    5)
        echo -e "${YELLOW}👋 Exiting without creating tag${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}❌ Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${YELLOW}📝 Creating version $new_version${NC}"

# Get description for the tag
read -p "Enter tag description (or press Enter for default): " tag_description

if [[ -z "$tag_description" ]]; then
    # Generate default description based on recent commits
    recent_commits=$(git log --oneline $latest_tag..HEAD | head -3 | sed 's/^[a-f0-9]* /- /')
    tag_description="Version $new_version

Recent changes:
$recent_commits"
fi

# Check if CHANGELOG.md has been updated recently
if git diff --name-only HEAD~3..HEAD | grep -q "CHANGELOG.md"; then
    echo -e "${GREEN}✅ CHANGELOG.md appears to be updated${NC}"
else
    echo -e "${YELLOW}⚠️  CHANGELOG.md may need updating${NC}"
    read -p "Continue anyway? (y/N): " continue_choice
    if [[ "$continue_choice" != "y" ]] && [[ "$continue_choice" != "Y" ]]; then
        echo -e "${YELLOW}👋 Please update CHANGELOG.md first${NC}"
        exit 1
    fi
fi

# Create the tag
echo -e "${BLUE}🏷️  Creating annotated tag $new_version${NC}"
git tag -a "$new_version" -m "$tag_description"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Tag $new_version created successfully!${NC}"
    echo ""
    echo -e "${GREEN}🚀 Next steps:${NC}"
    echo "1. Push your commits: ${BLUE}git push origin $current_branch${NC}"
    echo "2. Tags will be pushed automatically (followTags is enabled)"
    echo "3. Or push tags explicitly: ${BLUE}git push origin --tags${NC}"
    
    # Show the tag
    echo ""
    echo -e "${GREEN}📋 Tag details:${NC}"
    git show --stat $new_version
else
    echo -e "${RED}❌ Failed to create tag${NC}"
    exit 1
fi