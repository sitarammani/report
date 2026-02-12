# Flutter App Deployment Guide

## Prerequisites

```bash
# Verify Flutter setup
flutter doctor

# Update Flutter
flutter upgrade
```

---

## 1. ANDROID DEPLOYMENT

### Option A: Google Play Store

#### Step 1: Create Signing Key
```bash
cd /Users/janani/Desktop/sitapp/budgetapp/budgetui

# Generate keystore (one time only)
keytool -genkey -v -keystore ~/budgetapp.jks -keyalg RSA -keysize 2048 -validity 10000 -alias budgetapp

# Enter details:
# - Password: (create secure password)
# - First/Last Name: Your Name
# - Organizational Unit: Your Company
# - Organization: Your Company
# - City/Locality: Your City
# - State/Province: Your State
# - Country: US
```

#### Step 2: Configure Signing in Flutter
Create `android/key.properties`:
```properties
storePassword=YOUR_PASSWORD
keyPassword=YOUR_PASSWORD
keyAlias=budgetapp
storeFile=~/budgetapp.jks
```

Update `android/app/build.gradle`:
```gradle
signingConfigs {
    release {
        keyAlias keystoreProperties['keyAlias']
        keyPassword keystoreProperties['keyPassword']
        storeFile file(keystoreProperties['storeFile'])
        storePassword keystoreProperties['storePassword']
    }
}

buildTypes {
    release {
        signingConfig signingConfigs.release
    }
}
```

#### Step 3: Build Release APK/AAB
```bash
# Build AAB (recommended for Play Store)
flutter build appbundle --release

# Or build APK for testing/direct distribution
flutter build apk --release
```

Build output:
- **AAB**: `build/app/outputs/bundle/release/app-release.aab`
- **APK**: `build/app/outputs/apk/release/app-release.apk`

#### Step 4: Upload to Google Play Store
1. Go to [Google Play Console](https://play.google.com/console)
2. Create new app or select existing
3. Set up app details (description, screenshots, etc.)
4. Upload AAB file to Internal Testing > Release
5. Review and publish

---

### Option B: Direct APK Distribution
```bash
# Build debug APK for testing
flutter build apk --debug

# Build release APK for distribution
flutter build apk --release
```

Share `app-release.apk` directly - users can install via:
- Email attachment
- Cloud storage link
- QR code scanner

---

## 2. macOS DEPLOYMENT

### Option A: Mac App Store

#### Step 1: Create Apple Developer Account
- Sign up at [developer.apple.com](https://developer.apple.com)
- Enroll in Apple Developer Program ($99/year)
- Create App ID in Certificates, IDs & Profiles

#### Step 2: Configure App Info
Update `macos/Runner/GeneralInfo.plist`:
```xml
<key>CFBundleName</key>
<string>Budget App</string>
<key>CFBundleShortVersionString</key>
<string>1.0.0</string>
<key>CFBundleVersion</key>
<string>1</string>
```

Update `pubspec.yaml`:
```yaml
version: 1.0.0+1
```

#### Step 3: Build Release App
```bash
# Build macOS app
flutter build macos --release

# Output: build/macos/Build/Products/Release/budgetui.app
```

#### Step 4: Notarize for Mac App Store
```bash
# Create DMG for distribution
hdiutil create -volname "Budget App" -srcfolder build/macos/Build/Products/Release/budgetui.app -ov -format UDZO ~/Desktop/budgetapp.dmg

# Notarize (required for Big Sur+)
xcrun altool --notarize-app --file ~/Desktop/budgetapp.dmg --primary-bundle-id com.example.budgetapp -u your@email.com -p app-specific-password

# Wait for notarization to complete, then staple
xcrun stapler staple ~/Desktop/budgetapp.dmg
```

#### Step 5: Submit to Mac App Store
1. Open Xcode: `open macos/Runner.xcworkspace`
2. Select "Any Mac" as target
3. Product → Archive
4. Upload via Xcode Organizer

---

### Option B: Direct Distribution (No App Store)

#### Step 1: Create DMG Package
```bash
# Build release app
flutter build macos --release

# Create DMG
hdiutil create -volname "Budget App" -srcfolder build/macos/Build/Products/Release/budgetui.app -ov -format UDZO ~/Desktop/budgetapp.dmg
```

#### Step 2: Notarize App (Mac requirement)
```bash
# Generate app-specific password at appleid.apple.com

xcrun altool --notarize-app --file ~/Desktop/budgetapp.dmg \
  --primary-bundle-id com.example.budgetapp \
  -u your@email.com \
  -p your_app_specific_password

# Check status
xcrun altool --notarization-info REQUEST_UUID -u your@email.com -p your_app_specific_password

# Staple notarization ticket
xcrun stapler staple ~/Desktop/budgetapp.dmg
```

#### Step 3: Distribute via Website or Cloud
- Upload DMG to your website
- Users download and open

---

## 3. BUILD VARIANTS

### Debug Build
```bash
flutter build apk --debug         # Android
flutter build macos               # macOS
```

### Release Build
```bash
flutter build apk --release       # Android APK
flutter build appbundle --release # Android App Bundle (Play Store)
flutter build macos --release     # macOS
```

---

## 4. VERSION MANAGEMENT

Update in `pubspec.yaml`:
```yaml
version: 1.0.0+1
# bumped to: 1.0.1+2
```

Format: `major.minor.patch+build_number`

---

## 5. QUICK CHECKLIST

### Pre-Release
- [ ] Update version in `pubspec.yaml`
- [ ] Test on physical devices (Android & Mac)
- [ ] Update app description/screenshots
- [ ] Test CSV import with sample files
- [ ] Verify report generation works
- [ ] Check database persistence

### Android Release
- [ ] Create signing key (if not exists)
- [ ] Build AAB for Play Store
- [ ] Set up Google Play Console listing
- [ ] Upload privacy policy
- [ ] Configure pricing/distribution

### macOS Release
- [ ] Create Apple Developer account
- [ ] Generate signing certificate
- [ ] Build and notarize app
- [ ] Create DMG package
- [ ] Test on Mac before release

---

## 6. USEFUL COMMANDS

```bash
# Clean build
flutter clean
flutter pub get

# Analyze code
flutter analyze

# Run tests
flutter test

# Check dependencies
flutter pub outdated

# Generate build
flutter build apk --release
flutter build appbundle --release
flutter build macos --release
flutter build web --release
```

---

## 7. COMMON ISSUES & SOLUTIONS

### "App not optimized" warning
- Use AAB (App Bundle) for Play Store instead of APK

### macOS: "App cannot be opened"
- Run: `sudo xattr -rd com.apple.quarantine /path/to/app`

### Android: "Keystore password incorrect"
- Check `android/key.properties` file exists and has correct password
- Verify keystore file path is correct

### Flutter version mismatch
```bash
flutter pub get
flutter clean
flutter pub get
```

---

## Support & Resources

- [Flutter Documentation](https://docs.flutter.dev)
- [Google Play Console](https://play.google.com/console)
- [Mac App Store Connect](https://appstoreconnect.apple.com)
- [Apple Developer](https://developer.apple.com)
