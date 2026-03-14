import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Window {
    id: root
    visible: true
    width:  bridge ? Math.max(300, bridge.windowWidth) : 400
    height: bridge ? bridge.targetHeight : 200
    minimumWidth: 300
    minimumHeight: 120
    x: bridge ? bridge.windowX : 100
    y: bridge ? bridge.windowY : 100

    flags: Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
    color: "transparent"
    title: "Tuxile ActRunner"

    readonly property color primaryBg:  "#06060f"
    readonly property color surface:    "#0a0a18"
    readonly property color neonCyan:   "#00ffff"
    readonly property color neonPurple: "#9000ff"
    readonly property color neonGreen:  "#00ff88"
    readonly property color dangerRed:  "#ff4466"
    readonly property color primaryText:"#e8ffe8"
    readonly property color mutedText:  "#4a6a5a"
    readonly property color neonYellow: "#ffcc00"

    // Ctrl+Wheel → opacity
    WheelHandler {
        acceptedModifiers: Qt.ControlModifier
        onWheel: (event) => bridge.adjustOpacity(event.angleDelta.y > 0 ? 0.05 : -0.05)
    }

    // Background — dimmed by bridge.opacity, separate from content so text stays sharp
    Rectangle {
        anchors.fill: parent
        color: primaryBg
        opacity: bridge ? bridge.opacity : 0.85
    }

    // ── TITLEBAR ──────────────────────────────────────────────────────
    Rectangle {
        id: titleBar
        anchors.top: parent.top
        anchors.left: parent.left; anchors.right: parent.right
        height: 26
        color: surface

        Rectangle {
            anchors.bottom: parent.bottom
            anchors.left: parent.left; anchors.right: parent.right
            height: 1; color: Qt.rgba(0, 1, 1, 0.08)
        }

        // Ctrl+LMB → drag window
        MouseArea {
            anchors.fill: parent
            cursorShape: Qt.SizeAllCursor
            onPressed: (mouse) => { if (mouse.modifiers & Qt.ControlModifier) bridge.start_drag() }
        }

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 7; anchors.rightMargin: 7
            spacing: 4

            // Three dots
            Row {
                spacing: 4; Layout.alignment: Qt.AlignVCenter
                Rectangle { width: 7; height: 7; radius: 4; color: dangerRed  }
                Rectangle { width: 7; height: 7; radius: 4; color: neonYellow }
                Rectangle { width: 7; height: 7; radius: 4; color: neonGreen  }
            }

            Item { Layout.fillWidth: true }

            Text {
                text: "✦ TUXILE"; color: neonCyan
                font.family: "Orbitron"; font.pixelSize: 8; font.letterSpacing: 2
                Layout.alignment: Qt.AlignVCenter
            }

            Item { Layout.fillWidth: true }

            // A-
            Rectangle {
                width: tbAMinus.implicitWidth + 8; height: 16; radius: 2; color: "transparent"
                border.color: Qt.rgba(0, 1, 1, 0.15); border.width: 1
                Layout.alignment: Qt.AlignVCenter
                Text { id: tbAMinus; anchors.centerIn: parent; text: "A-"; color: mutedText; font.family: "Barlow Condensed"; font.pixelSize: 8 }
                MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onPressed: (m) => { if (m.modifiers & Qt.ControlModifier) bridge.decreaseFontSize() } }
            }

            // A+
            Rectangle {
                width: tbAPlus.implicitWidth + 8; height: 16; radius: 2; color: "transparent"
                border.color: Qt.rgba(0, 1, 1, 0.15); border.width: 1
                Layout.alignment: Qt.AlignVCenter
                Text { id: tbAPlus; anchors.centerIn: parent; text: "A+"; color: mutedText; font.family: "Barlow Condensed"; font.pixelSize: 8 }
                MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onPressed: (m) => { if (m.modifiers & Qt.ControlModifier) bridge.increaseFontSize() } }
            }

            // R (reset)
            Rectangle {
                width: tbR.implicitWidth + 8; height: 16; radius: 2; color: "transparent"
                border.color: rHover.containsMouse ? Qt.rgba(1, 0.27, 0.4, 0.5) : Qt.rgba(0, 1, 1, 0.15); border.width: 1
                Layout.alignment: Qt.AlignVCenter
                Text { id: tbR; anchors.centerIn: parent; text: "R"; color: rHover.containsMouse ? dangerRed : mutedText; font.family: "Barlow Condensed"; font.pixelSize: 8 }
                MouseArea { id: rHover; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onPressed: (m) => { if (m.modifiers & Qt.ControlModifier) bridge.resetProgress() } }
            }

            // ✕ (close)
            Rectangle {
                width: tbX.implicitWidth + 8; height: 16; radius: 2; color: "transparent"
                border.color: xHover.containsMouse ? Qt.rgba(1, 0.27, 0.4, 0.5) : Qt.rgba(0, 1, 1, 0.15); border.width: 1
                Layout.alignment: Qt.AlignVCenter
                Text { id: tbX; anchors.centerIn: parent; text: "✕"; color: xHover.containsMouse ? dangerRed : mutedText; font.family: "Barlow Condensed"; font.pixelSize: 8 }
                MouseArea { id: xHover; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onPressed: (m) => { if (m.modifiers & Qt.ControlModifier) Qt.quit() } }
            }
        }
    }

    // ── BODY (content + sidebar) ──────────────────────────────────────
    Item {
        id: bodyRow
        anchors.top: titleBar.bottom
        anchors.left: parent.left; anchors.right: parent.right
        anchors.bottom: parent.bottom

        // ── SIDEBAR (right, 22px) ─────────────────────────────────────
        Rectangle {
            id: sidebar
            anchors.top: parent.top; anchors.bottom: parent.bottom
            anchors.right: parent.right
            width: 22
            color: "#08081a"

            // Left border
            Rectangle {
                anchors.top: parent.top; anchors.bottom: parent.bottom; anchors.left: parent.left
                width: 1; color: Qt.rgba(0, 1, 1, 0.08)
            }

            // ▲ button
            Item {
                id: sidebarPrev
                anchors.top: parent.top
                width: parent.width; height: 22
                Text { anchors.centerIn: parent; text: "▲"; color: neonCyan; font.pixelSize: 11 }
                MouseArea {
                    anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                    onPressed: (m) => { if (m.modifiers & Qt.ControlModifier) bridge.onPrevStep() }
                }
            }

            // ▼ button
            Item {
                id: sidebarNext
                anchors.bottom: parent.bottom
                width: parent.width; height: 22
                Text { anchors.centerIn: parent; text: "▼"; color: neonCyan; font.pixelSize: 11 }
                MouseArea {
                    anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                    onPressed: (m) => { if (m.modifiers & Qt.ControlModifier) bridge.onNextStep() }
                }
            }

            // Percentage label
            Item {
                id: sidebarPct
                anchors.bottom: sidebarNext.top
                width: parent.width; height: 20
                Text {
                    anchors.centerIn: parent
                    text: {
                        var total = bridge.currentActTotalSteps
                        if (total <= 1) return "100%"
                        return Math.round(bridge.currentActStepIndex / (total - 1) * 100) + "%"
                    }
                    color: {
                        var total = bridge.currentActTotalSteps
                        var ratio = total > 1 ? bridge.currentActStepIndex / (total - 1) : 1.0
                        return ratio >= 0.9 ? neonGreen : neonCyan
                    }
                    font.family: "Barlow Condensed"; font.pixelSize: 7
                }
            }

            // Progress track (fills between ▲ and percentage label)
            Item {
                anchors.top: sidebarPrev.bottom
                anchors.bottom: sidebarPct.top
                width: parent.width

                Rectangle {
                    width: 4; radius: 2
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.top: parent.top; anchors.bottom: parent.bottom
                    anchors.topMargin: 4; anchors.bottomMargin: 4
                    color: "#1a1a2e"

                    // Fill from bottom: 0% at bottom → 100% at top
                    Rectangle {
                        width: parent.width; radius: 2
                        anchors.bottom: parent.bottom
                        height: {
                            var total = bridge.currentActTotalSteps
                            var ratio = total > 1 ? bridge.currentActStepIndex / (total - 1) : 1.0
                            return parent.height * ratio
                        }
                        gradient: Gradient {
                            GradientStop { position: 0.0; color: neonCyan   }
                            GradientStop { position: 1.0; color: neonYellow  }
                        }
                        Behavior on height { NumberAnimation { duration: 200 } }
                    }
                }
            }
        }

        // ── CONTENT AREA (left, fills) ────────────────────────────────
        Item {
            id: contentArea
            anchors.top: parent.top; anchors.bottom: parent.bottom
            anchors.left: parent.left; anchors.right: sidebar.left

            // TOP BAR
            Item {
                id: topBar
                anchors.top: parent.top
                anchors.left: parent.left; anchors.right: parent.right
                height: 22

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 8; anchors.rightMargin: 8
                    spacing: 0

                    Text {
                        text: "ACT " + bridge.currentActNumber
                        color: mutedText; font.family: "Barlow Condensed"; font.pixelSize: 8
                        font.weight: Font.DemiBold
                    }

                    Item { Layout.fillWidth: true }

                    Text {
                        text: bridge.stepZoneName
                        color: neonCyan; font.family: "Barlow Condensed"
                        font.weight: Font.DemiBold; font.pixelSize: bridge.baseFontSize + 1
                        font.letterSpacing: 1
                    }

                    Item { Layout.fillWidth: true }

                    Text {
                        text: (bridge.currentActStepIndex + 1) + "/" + bridge.currentActTotalSteps
                        color: neonPurple; font.family: "Barlow Condensed"; font.pixelSize: 8
                        font.weight: Font.DemiBold
                    }
                }

                // Divider below top bar
                Rectangle {
                    anchors.bottom: parent.bottom
                    anchors.left: parent.left; anchors.right: parent.right
                    height: 1; color: Qt.rgba(0, 1, 1, 0.08)
                }
            }

            // SUBSTEP LINES
            Column {
                id: substepList
                anchors.top: topBar.bottom
                x: 8
                width: contentArea.width - 16
                topPadding: 6; bottomPadding: 6
                spacing: 3

                // Warning shown when Client.txt is not configured
                Item {
                    visible: bridge.currentZone === "Waiting..."
                    width: substepList.width
                    height: visible ? 16 : 0
                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        text: "⚠ Log file not set — auto-tracking disabled"
                        color: neonYellow
                        font.family: "Barlow Condensed"; font.pixelSize: 8
                    }
                }

                Repeater {
                    model: bridge.substeps
                    delegate: Item {
                        width: substepList.width
                        height: bridge.baseFontSize + 6
                        clip: true

                        Row {
                            anchors.verticalCenter: parent.verticalCenter
                            spacing: 4

                            // Icon column
                            Text {
                                width: 16
                                anchors.verticalCenter: parent.verticalCenter
                                text: {
                                    if (modelData.isCompleted) return "✓"
                                    if (!modelData.isCurrent)  return "›"
                                    var t = modelData.iconType
                                    if (t === "waypoint") return "🔵"
                                    if (t === "boss")     return "⚔"
                                    if (t === "quest")    return "❗"
                                    if (t === "item")     return "📦"
                                    if (t === "trial")    return "🏆"
                                    if (t === "town")     return "🏠"
                                    if (t === "zone")     return "→"
                                    return "→"
                                }
                                color: {
                                    if (modelData.isCompleted) return mutedText
                                    if (modelData.isCurrent)   return neonCyan
                                    return mutedText
                                }
                                font.pixelSize: bridge.baseFontSize
                                font.family: "Barlow Condensed"
                                font.weight: Font.DemiBold
                            }

                            // Text column
                            Text {
                                width: substepList.width - 20
                                anchors.verticalCenter: parent.verticalCenter
                                text: modelData.text
                                color: {
                                    if (modelData.isCompleted) return mutedText
                                    if (modelData.isCurrent)   return primaryText
                                    return mutedText
                                }
                                opacity: modelData.isCompleted ? 0.3 : 1.0
                                font.family: "Barlow Condensed"
                                font.pixelSize: modelData.isCurrent
                                                ? bridge.baseFontSize
                                                : Math.max(8, bridge.baseFontSize - 1)
                                font.weight: Font.DemiBold
                                textFormat: Text.RichText
                                clip: true
                            }
                        }

                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            onPressed: (mouse) => {
                                if (mouse.modifiers & Qt.ControlModifier)
                                    bridge.onSubstepClicked(index)
                            }
                        }
                    }
                }
            }
        }
    }

} // Window
