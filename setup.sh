#!/bin/bash

echo "🔍 Setting up the Investigation Case Manager..."

# Step 1: Clone the repo into 'Investigations'
if [ -d "Investigations" ]; then
  echo "📁 Folder 'Investigations' already exists. Skipping clone."
else
  echo "📦 Cloning repo into 'Investigations'..."
  git clone https://github.com/IOCOfficial/CaseManagement.git Investigations
fi

# Step 2: Navigate into folder
cd Investigations || { echo "❌ Failed to enter Investigations directory."; exit 1; }

# Step 3: Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Step 4: Optional - Launch script
echo
read -p "🚀 Do you want to launch the app now? (y/n): " launch
if [[ "$launch" == "y" ]]; then
  echo "▶️ Launching Case Manager..."
  python3 main.py
else
  echo "✅ Setup complete. Run the app later using: python3 main.py"
fi
