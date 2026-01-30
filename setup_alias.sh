#!/bin/bash
# Setup script to alias ls to reader-ls
#
# Usage:
#   1. Source this file in your shell:
#      source setup_alias.sh
#
#   2. Or add to your ~/.bashrc or ~/.zshrc:
#      alias ls='reader-ls'
#
# To make it permanent, add the alias line to your shell configuration file.

# Create the alias
alias ls='reader-ls'

echo "✓ Alias created: ls -> reader-ls"
echo ""
echo "To make this permanent, add this line to your ~/.bashrc or ~/.zshrc:"
echo "  alias ls='reader-ls'"
echo ""
echo "Test it by running: ls"
