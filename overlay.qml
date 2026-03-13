import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Window {
    id: root
    visible: true
    width: bridge ? Math.max(300, bridge.windowWidth) : 400
    // Height driven by QML content chain: ColumnLayout.implicitHeight sums children's implicitHeight
    height: titleBar.height + bodyColumn.implicitHeight + 16 + 2
    x: bridge ? bridge.windowX : 100
    y: bridge ? bridge.windowY : 100

    flags: Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
    color: "transparent"
    title: "TuxileOverlay"

    property color primaryBg:  "#06060f"
    property color titleBg:    "#0d0d1a"
    property color cardBg:     "#0d0d20"
    property color neonCyan:   "#00ffff"
    property color neonPurple: "#9000ff"
    property color neonGreen:  "#00ff88"
    property color dangerRed:  "#ff4466"
    property color primaryText:"#e8ffe8"
    property color mutedText:  "#4a6a5a"
    property color neonYellow: "#ffcc00"

    // Ctrl+Wheel → opacity
    WheelHandler {
        acceptedModifiers: Qt.ControlModifier
        onWheel: (event) => bridge.adjustOpacity(event.angleDelta.y > 0 ? 0.05 : -0.05)
    }

    // ── Outer border + corner markers ────────────────────────────────
    Rectangle {
        anchors.fill: parent
        color: "transparent"
        border.color: Qt.rgba(0, 1, 1, 0.25)
        border.width: 1

        Rectangle { width:4; height:4; color:neonCyan; anchors.top:parent.top;    anchors.left:parent.left   }
        Rectangle { width:4; height:4; color:neonCyan; anchors.top:parent.top;    anchors.right:parent.right }
        Rectangle { width:4; height:4; color:neonCyan; anchors.bottom:parent.bottom; anchors.left:parent.left   }
        Rectangle { width:4; height:4; color:neonCyan; anchors.bottom:parent.bottom; anchors.right:parent.right }
    }

    // ── TITLE BAR ────────────────────────────────────────────────────
    Rectangle {
        id: titleBar
        x: 1; y: 1
        width: root.width - 2
        height: 28
        color: titleBg

        // Bottom border line
        Rectangle {
            anchors.bottom: parent.bottom
            anchors.left: parent.left; anchors.right: parent.right
            height: 1
            color: Qt.rgba(0, 1, 1, 0.1)
        }

        // Ctrl+LMB drag
        MouseArea {
            anchors.fill: parent
            cursorShape: Qt.SizeAllCursor
            onPressed: (mouse) => { if (mouse.modifiers & Qt.ControlModifier) bridge.start_drag() }
        }

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 8; anchors.rightMargin: 8
            spacing: 5

            // Three dots
            Row {
                spacing: 5
                Layout.alignment: Qt.AlignVCenter
                Rectangle { width:8; height:8; radius:4; color:dangerRed  }
                Rectangle { width:8; height:8; radius:4; color:neonYellow }
                Rectangle { width:8; height:8; radius:4; color:neonGreen  }
            }

            Item { Layout.fillWidth: true }

            Text {
                text: "✦ TUXILE"
                color: neonCyan
                font.family: "Orbitron"; font.pixelSize: 9
                font.letterSpacing: 2
                Layout.alignment: Qt.AlignVCenter
            }

            Item { Layout.fillWidth: true }

            // A- button
            Rectangle {
                width:24; height:18; radius:2; color:"transparent"
                border.color: Qt.rgba(0,1,1,0.3); border.width:1
                Layout.alignment: Qt.AlignVCenter
                Text { anchors.centerIn:parent; text:"A-"; color:neonCyan; font.family:"Share Tech Mono"; font.pixelSize:8 }
                MouseArea { anchors.fill:parent; cursorShape:Qt.PointingHandCursor; onPressed: (mouse) => { if (mouse.modifiers & Qt.ControlModifier) bridge.decreaseFontSize() } }
            }

            // A+ button
            Rectangle {
                width:24; height:18; radius:2; color:"transparent"
                border.color: Qt.rgba(0,1,1,0.3); border.width:1
                Layout.alignment: Qt.AlignVCenter
                Text { anchors.centerIn:parent; text:"A+"; color:neonCyan; font.family:"Share Tech Mono"; font.pixelSize:8 }
                MouseArea { anchors.fill:parent; cursorShape:Qt.PointingHandCursor; onPressed: (mouse) => { if (mouse.modifiers & Qt.ControlModifier) bridge.increaseFontSize() } }
            }

            // R button (reset)
            Rectangle {
                width:20; height:18; radius:2; color:"transparent"
                border.color: rArea.containsMouse ? Qt.rgba(1,0.27,0.4,0.5) : Qt.rgba(0.29,0.42,0.35,0.4)
                border.width:1
                Layout.alignment: Qt.AlignVCenter
                Text { anchors.centerIn:parent; text:"R"; color: rArea.containsMouse ? dangerRed : mutedText; font.family:"Share Tech Mono"; font.pixelSize:8 }
                MouseArea { id:rArea; anchors.fill:parent; hoverEnabled:true; cursorShape:Qt.PointingHandCursor; onPressed: (mouse) => { if (mouse.modifiers & Qt.ControlModifier) bridge.resetProgress() } }
            }

            // ✕ button
            Rectangle {
                width:20; height:18; radius:2; color:"transparent"
                border.color: Qt.rgba(1,0.27,0.4,0.3); border.width:1
                Layout.alignment: Qt.AlignVCenter
                Text { anchors.centerIn:parent; text:"✕"; color:dangerRed; font.family:"Share Tech Mono"; font.pixelSize:9 }
                MouseArea { anchors.fill:parent; cursorShape:Qt.PointingHandCursor; onPressed: (mouse) => { if (mouse.modifiers & Qt.ControlModifier) Qt.quit() } }
            }
        }
    }

    // ── BODY BACKGROUND (opacity-controlled) ─────────────────────────
    Rectangle {
        x: 1
        y: titleBar.y + titleBar.height
        width: root.width - 2
        height: root.height - titleBar.y - titleBar.height - 1
        color: primaryBg
        opacity: bridge.opacity
    }

    // ── BODY CONTENT ─────────────────────────────────────────────────
    // Separate from bodyBg so opacity doesn't affect text readability
    // (opacity on a parent dims children too — we want background dim only)
    // Solution: multiply primaryBg alpha by bridge.opacity instead
    // The Rectangle above handles the dimmed background; this column is opaque.
    ColumnLayout {
        id: bodyColumn
        x: 8 + 1                                // 1px border + 8px padding
        y: titleBar.y + titleBar.height + 8     // 8px top padding
        width: root.width - 16 - 2              // subtract left+right padding and borders
        spacing: 6

        // ── TOP BAR ──────────────────────────────────────────────────
        RowLayout {
            Layout.fillWidth: true
            spacing: 4

            Text {
                text: "ACT " + bridge.currentActNumber
                color: mutedText
                font.family: "Share Tech Mono"; font.pixelSize: 9
            }

            Item { Layout.fillWidth: true }

            Text {
                text: bridge.stepZoneName
                color: neonCyan
                font.family: "Share Tech Mono"
                font.bold: true
                font.pixelSize: bridge.baseFontSize + 2
                font.letterSpacing: 1
            }

            Item { Layout.fillWidth: true }

            Text {
                text: (bridge.currentActStepIndex + 1) + " / " + bridge.currentActTotalSteps
                color: neonPurple
                font.family: "Share Tech Mono"; font.pixelSize: 9
            }
        }

        // ── DIVIDER ──────────────────────────────────────────────────
        Rectangle {
            Layout.fillWidth: true; height: 1
            color: Qt.rgba(0, 1, 1, 0.1)
        }

        // ── CARD A: COMPLETED ─────────────────────────────────────────
        Rectangle {
            Layout.fillWidth: true
            visible: bridge.currentStepIndex > 0 && bridge.baseFontSize < 14
            implicitHeight: cardACol.implicitHeight + 12
            color: cardBg
            border.color: Qt.rgba(0, 1, 0.53, 0.15); border.width: 1
            radius: 4

            Column {
                id: cardACol
                anchors.top: parent.top; anchors.left: parent.left; anchors.right: parent.right
                anchors.topMargin: 6; anchors.leftMargin: 8; anchors.rightMargin: 8
                spacing: 3

                Text {
                    text: "✓ COMPLETED"
                    color: neonGreen
                    font.family: "Share Tech Mono"; font.pixelSize: 8
                }
                Text {
                    width: parent.width
                    text: bridge.previousSubstep
                    color: mutedText
                    font.family: "Share Tech Mono"
                    font.pixelSize: Math.max(8, bridge.baseFontSize - 1)
                    wrapMode: Text.WordWrap
                    textFormat: Text.RichText
                }
            }
        }

        // ── CARD B: CURRENT OBJECTIVE ─────────────────────────────────
        Rectangle {
            Layout.fillWidth: true
            implicitHeight: cardBCol.implicitHeight + 12
            color: cardBg
            border.color: Qt.rgba(0, 1, 1, 0.45); border.width: 1
            radius: 4

            Column {
                id: cardBCol
                anchors.top: parent.top; anchors.left: parent.left; anchors.right: parent.right
                anchors.topMargin: 6; anchors.leftMargin: 8; anchors.rightMargin: 8
                spacing: 4

                Text {
                    text: "▶ CURRENT OBJECTIVE"
                    color: neonCyan
                    font.family: "Share Tech Mono"; font.pixelSize: 8
                }

                Repeater {
                    model: bridge.substeps
                    delegate: Text {
                        width: cardBCol.width
                        // Completed: strip HTML, show ✓ prefix, muted color
                        // Active: keep HTML spans for coloured keywords
                        text: modelData.isCompleted
                              ? "✓ " + modelData.text.replace(/<[^>]+>/g, "")
                              : modelData.text
                        color: modelData.isCompleted ? mutedText : primaryText
                        font.family: "Share Tech Mono"
                        font.pixelSize: bridge.baseFontSize
                        wrapMode: Text.WordWrap
                        textFormat: modelData.isCompleted ? Text.PlainText : Text.RichText

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

        // ── CARD C: NEXT ──────────────────────────────────────────────
        Rectangle {
            Layout.fillWidth: true
            visible: bridge.currentStepIndex < bridge.totalSteps - 1 && bridge.baseFontSize < 14
            implicitHeight: cardCCol.implicitHeight + 12
            color: cardBg
            border.color: Qt.rgba(0.56, 0, 1, 0.2); border.width: 1
            radius: 4

            Column {
                id: cardCCol
                anchors.top: parent.top; anchors.left: parent.left; anchors.right: parent.right
                anchors.topMargin: 6; anchors.leftMargin: 8; anchors.rightMargin: 8
                spacing: 3

                Text {
                    text: "NEXT"
                    color: neonPurple
                    font.family: "Share Tech Mono"; font.pixelSize: 8
                }
                Text {
                    width: parent.width
                    text: bridge.nextSubstep
                    color: mutedText
                    font.family: "Share Tech Mono"
                    font.pixelSize: Math.max(8, bridge.baseFontSize - 1)
                    wrapMode: Text.WordWrap
                    textFormat: Text.RichText
                }
            }
        }

        // ── FOOTER ────────────────────────────────────────────────────
        RowLayout {
            Layout.fillWidth: true
            spacing: 0

            // PREV ◀
            Rectangle {
                width: 44; height: 36; radius: 3
                color: prevArea.containsMouse ? Qt.rgba(0,1,1,0.12) : Qt.rgba(0,1,1,0.05)
                border.color: Qt.rgba(0,1,1,0.3); border.width: 1
                opacity: bridge.currentStepIndex > 0 ? 1.0 : 0.3
                Text {
                    anchors.centerIn: parent; text: "◀"
                    color: neonCyan; font.bold: true; font.pixelSize: 14
                }
                MouseArea {
                    id: prevArea
                    anchors.fill: parent; hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onPressed: (mouse) => {
                        if ((mouse.modifiers & Qt.ControlModifier) && bridge.currentStepIndex > 0)
                            bridge.onPrevStep()
                    }
                }
            }

            // Progress (center)
            Item {
                Layout.fillWidth: true
                height: 36

                Column {
                    anchors.centerIn: parent
                    width: parent.width - 8
                    spacing: 4

                    RowLayout {
                        width: parent.width
                        Text {
                            text: "ACT " + bridge.currentActNumber + " PROGRESS"
                            color: neonYellow; font.family: "Share Tech Mono"; font.pixelSize: 8
                        }
                        Item { Layout.fillWidth: true }
                        Text {
                            text: (bridge.currentActStepIndex + 1) + " / " + bridge.currentActTotalSteps
                            color: neonCyan; font.family: "Share Tech Mono"; font.pixelSize: 8
                        }
                    }

                    Rectangle {
                        width: parent.width; height: 3; radius: 1
                        color: "#1a1a2e"
                        Rectangle {
                            height: parent.height; radius: 1
                            width: parent.width * (bridge.currentActTotalSteps > 1
                                   ? (bridge.currentActStepIndex / (bridge.currentActTotalSteps - 1))
                                   : 1.0)
                            gradient: Gradient {
                                orientation: Gradient.Horizontal
                                GradientStop { position: 0.0; color: neonYellow }
                                GradientStop { position: 1.0; color: neonCyan }
                            }
                            Behavior on width { NumberAnimation { duration: 300; easing.type: Easing.OutQuad } }
                        }
                    }
                }
            }

            // NEXT ▶
            Rectangle {
                width: 44; height: 36; radius: 3
                color: nextArea.containsMouse ? Qt.rgba(0,1,1,0.12) : Qt.rgba(0,1,1,0.05)
                border.color: Qt.rgba(0,1,1,0.3); border.width: 1
                opacity: bridge.currentStepIndex < bridge.totalSteps - 1 ? 1.0 : 0.3
                Text {
                    anchors.centerIn: parent; text: "▶"
                    color: neonCyan; font.bold: true; font.pixelSize: 14
                }
                MouseArea {
                    id: nextArea
                    anchors.fill: parent; hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onPressed: (mouse) => {
                        if ((mouse.modifiers & Qt.ControlModifier) && bridge.currentStepIndex < bridge.totalSteps - 1)
                            bridge.onNextStep()
                    }
                }
            }
        }

    } // bodyColumn

} // Window
