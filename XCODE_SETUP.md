# ⚠️ macOS Build Setup Required

## Issue
Xcode is not installed. It's required to build Flutter apps for macOS.

## Solution 1: Install Xcode from App Store (Recommended)

```bash
# Open App Store and search for "Xcode"
# Or click this link:
open "macappstore://apps.apple.com/app/xcode/id497799835"

# After installation, activate command line tools:
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer

# Accept Xcode license
sudo xcodebuild -runFirstLaunch

# Verify installation
xcodebuild -version
```

**Time**: ~30-45 minutes (large download ~12GB)

---

## Solution 2: Install via Command Line (Faster Alternative)

```bash
# Install Xcode command line tools only
xcode-select --install

# Accept license when prompted
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
sudo xcodebuild -runFirstLaunch

# Verify
xcode-select -p
```

---

## After Installation - Build macOS App

```bash
cd /Users/janani/Desktop/sitapp/budgetapp/budgetui

# Clean prev build
flutter clean

# Get dependencies
flutter pub get

# Build release app
flutter build macos --release

# Output will be at:
# build/macos/Build/Products/Release/budgetui.app (App)
# or build/macos/Build/Products/Release/Budget\ App.app
```

---

## Creating DMG Package (After Successful Build)

```bash
# Create DMG file for distribution
hdiutil create -volname "Budget App" \
  -srcfolder build/macos/Build/Products/Release/budgetui.app \
  -ov -format UDZO \
  ~/Desktop/budgetapp.dmg
```

---

## Check Current Xcode Status

```bash
# Verify tools are available
which xcode-select
which xcodebuild
xcode-select -p

# Run doctor to check setup
flutter doctor
```

---

## Recommended: Install via Homebrew

```bash
# If you have Homebrew installed
brew install --cask xcode

# After installation
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
```

---

## Troubleshooting

### "Xcode is locked"
- Go to Applications → Right-click Xcode → Click "Open"

### "Too old" or "License not accepted"
```bash
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
sudo xcodebuild -license accept -free
```

### Clear cache and retry
```bash
flutter clean
rm -rf build/
flutter pub get
flutter build macos --release
```

---

## Next Steps
1. ✅ Install Xcode (App Store or Command Line Tools)
2. ⏳ Wait for installation to complete
3. ⚙️ Run setup commands above
4. 🔨 Build app with: `flutter build macos --release`
5. 📦 Create DMG: `hdiutil create -volname "Budget App" ...`
6. ✨ Your macOS app is ready to distribute!
