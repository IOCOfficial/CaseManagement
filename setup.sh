#!/bin/bash

echo "🔍 Setting up the Investigation Case Manager..."

# === 1. Clone the repo ===
if [ -d "Investigations" ]; then
  echo "📁 Folder 'Investigations' already exists. Skipping clone."
else
  echo "📦 Cloning repo into 'Investigations'..."
  git clone https://github.com/IOCOfficial/CaseManagement.git Investigations
fi

# === 2. Move into folder ===
cd Investigations || { echo "❌ Failed to enter Investigations directory."; exit 1; }

# === 3. Install Python dependencies ===
echo "📦 Installing Python dependencies..."
if pip3 install -r requirements.txt; then
  echo "✅ Python dependencies installed successfully."
else
  echo "❌ Failed to install dependencies. Try running:"
  echo "   pip3 install -r requirements.txt"
  exit 1
fi

# === 4. Ensure vault_template exists ===
VAULT_TEMPLATE_DIR=~/vault_template/.obsidian

if [ ! -d "$VAULT_TEMPLATE_DIR" ]; then
  echo "📁 No vault template found at: $VAULT_TEMPLATE_DIR"
  read -p "➕ Would you like to create it now? (y/n): " create_vault
  if [[ "$create_vault" == "y" ]]; then
    mkdir -p "$VAULT_TEMPLATE_DIR"
    echo "✅ Created vault template directory."

    echo "📌 Now copy your preferred Obsidian vault's '.obsidian' folder into:"
    echo "   $VAULT_TEMPLATE_DIR"
    echo "   Example:"
    echo "   cp -R \"/path/to/your/vault/.obsidian\" ~/vault_template/"
  else
    echo "⚠️ Skipping vault template setup. You can add it manually later at:"
    echo "   $VAULT_TEMPLATE_DIR"
  fi
else
  echo "📁 Obsidian vault template already exists: $VAULT_TEMPLATE_DIR"
fi

# === 5. Launch the app ===
echo
read -p "🚀 Do you want to launch the Case Manager now? (y/n): " launch
if [[ "$launch" == "y" ]]; then
  echo "▶️ Launching Case Manager..."
  python3 caseManager.py
else
  echo "✅ Setup complete. Run the app anytime using: python3 caseManager.py"
fi
