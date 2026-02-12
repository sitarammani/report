# macOS Deployment - Step by Step

## Step 1: Update App Version

Update `pubspec.yaml`:
```yaml
name: pythonexpenseapp
version: 1.0.0+1
```

## Step 2: Generate macOS Platform
```bash
cd budgetui
flutter create --platforms macos .
```

## Step 3: Configure App Information

### Update macOS App Name and Bundle ID

**File: `macos/Runner/Configs/Config.xcconfig`**

Add or update:
```xcconfig
// Product name (displayed to users)
PRODUCT_NAME = Budget App

// Bundle ID (must be unique)
BUNDLE_ID = com.yourcompany.budgetapp
```

**File: `macos/Runner.xcodeproj/project.pbxproj`**
- Open in Xcode: `open macos/Runner.xcworkspace`
- Select Runner → Targets → Runner
- General tab → Bundle Identifier: `com.yourcompany.budgetapp`

## Step 4: Build Release App
```bash
flutter build macos --release
```

Output: `build/macos/Build/Products/Release/budgetui.app`

## Step 5: Create DMG Package
```bash
# Create DMG for distribution
hdiutil create -volname "Budget App" \
  -srcfolder build/macos/Build/Products/Release/budgetui.app \
  -ov -format UDZO ~/Desktop/budgetapp.dmg
```

## Step 6: Notarize App (Required for Big Sur+)

### Option A: With Apple Developer Account (Recommended)

```bash
# 1. Generate App-Specific Password at appleid.apple.com
# - Go to appleid.apple.com
# - Sign in
# - Security → App-Specific Passwords
# - Generate password for "macOS notarization"

# 2. Notarize the DMG
xcrun notarytool submit ~/Desktop/budgetapp.dmg \
  --apple-id your@email.com \
  --team-id TEAMID \
  --password app-specific-password

# 3. Get Request UUID, wait for completion
xcrun notarytool history --apple-id your@email.com

# 4. Check status
xcrun notarytool log REQUEST-UUID --apple-id your@email.com

# 5. Once approved, staple the ticket
xcrun stapler staple ~/Desktop/budgetapp.dmg
```

### Option B: Without Apple Developer Account (Alternative)
- Users can run: `sudo xattr -rd com.apple.quarantine /Applications/Budget\ App.app`

## Step 7: Distribute

### Direct Distribution
1. Upload `budgetapp.dmg` to your website
2. Share download link with users
3. Users download and install by:
   - Opening DMG
   - Dragging app to Applications folder

### Mac App Store
1. Create [Mac App Store Connect](https://appstoreconnect.apple.com) account
2. Register app in App Store Connect
3. Upload notarized app via Xcode:
   ```bash
   open macos/Runner.xcworkspace
   # Product → Archive → Upload to App Store
   ```

## Troubleshooting

### "App cannot be opened"
```bash
# Codesign the app
codesign -s - build/macos/Build/Products/Release/budgetui.app

# Or remove quarantine
sudo xattr -rd com.apple.quarantine build/macos/Build/Products/Release/budgetui.app
```

### "Bundle ID issues"
```bash
# Check current bundle ID
mdls -name kMDItemCFBundleIdentifier build/macos/Build/Products/Release/budgetui.app
```

### Rebuild if needed
```bash
flutter clean
flutter pub get
flutter build macos --release
```

## Version Bumping

For next release, update:
```yaml
version: 1.0.1+2  # major.minor.patch+build_number
```

Then rebuild: `flutter build macos --release`
