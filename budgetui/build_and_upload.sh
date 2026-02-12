#!/bin/bash

# Budget App Build & Upload Script

echo "═══════════════════════════════════════════"
echo "  Budget App - Build & Upload Tool"
echo "═══════════════════════════════════════════"
echo ""

# Check Flutter installation
if ! command -v flutter &> /dev/null; then
    echo "❌ Flutter not installed. Please install Flutter first."
    exit 1
fi

echo "✅ Flutter detected: $(flutter --version)"
echo ""

# Menu
echo "Select platform to build:"
echo "1) Android (APK)"
echo "2) Android (App Bundle for Play Store)"
echo "3) macOS"
echo "4) All (Android APK + macOS)"
echo ""
read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "Building Android APK (Release)..."
        flutter clean
        flutter pub get
        flutter build apk --release
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "✅ Build successful!"
            echo "📦 Output: build/app/outputs/apk/release/app-release.apk"
            echo ""
            read -p "Open output folder? (y/n): " open_folder
            if [ "$open_folder" = "y" ]; then
                open build/app/outputs/apk/release/
            fi
        fi
        ;;
    
    2)
        echo ""
        echo "Building Android App Bundle (Play Store)..."
        flutter clean
        flutter pub get
        flutter build appbundle --release
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "✅ Build successful!"
            echo "📦 Output: build/app/outputs/bundle/release/app-release.aab"
            echo ""
            echo "Next steps:"
            echo "1. Go to https://play.google.com/console"
            echo "2. Create/Select your app"
            echo "3. Upload AAB to Internal Testing or Release track"
            echo ""
            read -p "Open Google Play Console? (y/n): " open_console
            if [ "$open_console" = "y" ]; then
                open "https://play.google.com/console"
            fi
        fi
        ;;
    
    3)
        echo ""
        echo "Building macOS App (Release)..."
        flutter clean
        flutter pub get
        flutter build macos --release
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "✅ Build successful!"
            echo "📦 Output: build/macos/Build/Products/Release/budgetui.app"
            echo ""
            
            read -p "Create DMG package? (y/n): " create_dmg
            if [ "$create_dmg" = "y" ]; then
                DMG_FILE="$HOME/Desktop/budgetapp.dmg"
                echo "Creating DMG at $DMG_FILE..."
                hdiutil create -volname "Budget App" -srcfolder build/macos/Build/Products/Release/budgetui.app -ov -format UDZO "$DMG_FILE"
                
                if [ $? -eq 0 ]; then
                    echo "✅ DMG created successfully!"
                    echo "📦 Output: $DMG_FILE"
                    echo ""
                    echo "Next: Notarize the app for Mac distribution"
                    open "$HOME/Desktop/"
                fi
            fi
        fi
        ;;
    
    4)
        echo ""
        echo "Building for Android (APK) and macOS..."
        
        # Android APK
        echo "📱 Building Android APK..."
        flutter clean
        flutter pub get
        flutter build apk --release
        
        if [ $? -eq 0 ]; then
            echo "✅ Android APK built"
        else
            echo "❌ Android build failed"
            exit 1
        fi
        
        # macOS
        echo ""
        echo "🍎 Building macOS app..."
        flutter build macos --release
        
        if [ $? -eq 0 ]; then
            echo "✅ macOS app built"
        else
            echo "❌ macOS build failed"
            exit 1
        fi
        
        echo ""
        echo "✅ All builds completed!"
        echo ""
        echo "📦 Android APK: build/app/outputs/apk/release/app-release.apk"
        echo "📦 macOS App: build/macos/Build/Products/Release/budgetui.app"
        ;;
    
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "═══════════════════════════════════════════"
echo "  Build complete! 🎉"
echo "═══════════════════════════════════════════"
