#!/bin/bash

# Weilchain Counter Applet Interaction Script

APPLET_ADDRESS=${1:-"counter_applet_address_here"}

if [ "$APPLET_ADDRESS" = "counter_applet_address_here" ]; then
    echo "❌ Please provide the deployed applet address"
    echo "Usage: ./interact.sh <applet_address>"
    exit 1
fi

echo "🔗 Interacting with Counter Applet at: $APPLET_ADDRESS"
echo ""

# Initialize the counter (if not already done)
echo "🏁 Initializing counter..."
# weilchain call $APPLET_ADDRESS init --args '["alice"]'

echo "📊 Getting current count..."
# weilchain call $APPLET_ADDRESS get_count

echo "⬆️  Incrementing counter..."
# weilchain call $APPLET_ADDRESS increment

echo "⬆️  Incrementing counter again..."
# weilchain call $APPLET_ADDRESS increment

echo "➕ Adding 5 to counter..."
# weilchain call $APPLET_ADDRESS add --args '[5]'

echo "📊 Getting current count..."
# weilchain call $APPLET_ADDRESS get_count

echo "⬇️  Decrementing counter..."
# weilchain call $APPLET_ADDRESS decrement

echo "🔢 Setting counter to 100..."
# weilchain call $APPLET_ADDRESS set_count --args '[100]'

echo "📊 Getting current count..."
# weilchain call $APPLET_ADDRESS get_count

echo "🔄 Resetting counter..."
# weilchain call $APPLET_ADDRESS reset

echo "📊 Final count..."
# weilchain call $APPLET_ADDRESS get_count

echo "👤 Getting owner..."
# weilchain call $APPLET_ADDRESS get_owner

echo "📋 Getting full state..."
# weilchain call $APPLET_ADDRESS get_state

echo ""
echo "✅ Interaction complete!"