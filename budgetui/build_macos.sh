#!/bin/bash

echo "🍎 macOS Build Script - Budget App"
echo "=================================="
echo ""

cd /Users/janani/Desktop/sitapp/budgetapp/budgetui

echo "1️⃣ Checking Xcode installation..."
if xcodebuild -version &> /dev/null; then
    echo "✅ Xcode is ready"
else
    echo "❌ Xcode not ready yet. Please wait for installation to complete."
    exit 1
fi

echo ""
echo "2️⃣ Cleaning previous builds..."
flutter clean
rm -rf build/

echo ""
echo "3️⃣ Getting dependencies..."
flutter pub get

echo ""
echo "4️⃣ Building macOS release app..."
flutter build macos --release

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build successful!"
    
    APP_PATH="build/macos/Build/Products/Release/budgetui.app"
    if [ -d "$APP_PATH" ]; then
        echo "📱 App location: $APP_PATH"
        echo ""
        echo "5️⃣ Creating DMG package..."
        
        DMG_FILE="$HOME/Desktop/budgetapp.dmg"
        hdiutil create -volname "Budget App" \
            -srcfolder "$APP_PATH" \
            -ov -format UDZO "$DMG_FILE"
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "✅ DMG created successfully!"
            echo "📦 DMG location: $DMG_FILE"
            echo ""
            echo "================================"
            echo "🎉 macOS app is ready to distribute!"
            echo "================================"
            echo ""
            echo "Next steps:"
            echo "1. Test the app: open \"$APP_PATH\""
            echo "2. Share DMG: $DMG_FILE"
            echo "3. Or upload to Mac App Store"
        else
            echo "❌ DMG creation failed"
            exit 1
        fi
    else
        echo "❌ App not found at expected location"
        exit 1
    fi
else
    echo "❌ Build failed"
    exit 1
fi
