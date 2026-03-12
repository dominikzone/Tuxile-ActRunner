import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
// QtQuick.Effects removed — no MultiEffect in use

Window {
    id: root
    visible: true
    width: bridge.windowWidth
    height: bridge.windowHeight
    x: bridge.windowX
    y: bridge.windowY

    flags: bridge.clickThrough
           ? (Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowTransparentForInput)
           : (Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

    color: "transparent"
    title: "TuxileOverlay"


    property color primaryBg:   "#06060f"
    property color surface:     "#1a1a2e"
    property color neonCyan:    "#00ffff"
    property color neonPurple:  "#9000ff"
    property color neonGreen:   "#00ff88"
    property color dangerRed:   "#ff4466"
    property color primaryText: "#e8ffe8"
    property color mutedText:   "#4a6a5a"
    property color neonYellow:  "#ffcc00"

    property real glowOpacity: 1.0
    SequentialAnimation on glowOpacity {
        loops: Animation.Infinite; running: true
        NumberAnimation { from: 0.6; to: 1.0; duration: 2000 }
        NumberAnimation { from: 1.0; to: 0.6; duration: 2000 }
    }

    property bool cursorVisible: true
    Timer {
        interval: 500; running: true; repeat: true
        onTriggered: cursorVisible = !cursorVisible
    }

    // ── Ctrl+LMB anywhere: move window (DragHandler doesn't steal clicks from buttons) ──
    DragHandler {
        id: windowMoveHandler
        acceptedModifiers: Qt.ControlModifier
        acceptedButtons: Qt.LeftButton
        dragThreshold: 0
        target: null
        property point lastPos
        property bool isResize: false

        onActiveChanged: {
            if (active) {
                // If press landed in bottom-right resize corner, let resizeHandle take over
                isResize = centroid.pressPosition.x > root.width - 40 &&
                           centroid.pressPosition.y > root.height - 40
                if (!isResize) lastPos = centroid.position
            } else {
                bridge.updateWindowPos(root.x, root.y)
                bridge.updateWindowSize(root.width, root.height)
                bridge.save_config_to_disk()
            }
        }
        onCentroidChanged: {
            if (!active || isResize) return
            root.x += centroid.position.x - lastPos.x
            root.y += centroid.position.y - lastPos.y
            lastPos = centroid.position
        }
    }

    // ── Ctrl+Wheel: adjust window opacity ────────────────────────────────
    WheelHandler {
        acceptedModifiers: Qt.ControlModifier
        onWheel: (event) => bridge.adjustOpacity(event.angleDelta.y > 0 ? 0.05 : -0.05)
    }

    // ── Bottom-right 40×40 px corner: Ctrl+LMB drag to resize ────────────
    MouseArea {
        id: resizeHandle
        width: 40; height: 40
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        z: 20
        property point lastPos

        onPressed: (mouse) => {
            if (mouse.modifiers & Qt.ControlModifier)
                lastPos = Qt.point(mouse.x, mouse.y)
            else
                mouse.accepted = false
        }
        onPositionChanged: (mouse) => {
            if (!(mouse.buttons & Qt.LeftButton)) return
            let dx = mouse.x - lastPos.x
            let dy = mouse.y - lastPos.y
            root.width  = Math.max(280, root.width  + dx)
            root.height = Math.max(150, root.height + dy)
            lastPos = Qt.point(mouse.x, mouse.y)
        }
        onReleased: {
            bridge.updateWindowSize(root.width, root.height)
            bridge.save_config_to_disk()
        }
    }

    // ── Main container ────────────────────────────────────────────
    Rectangle {
        id: mainContainer
        anchors.fill: parent
        color: primaryBg
        opacity: bridge.opacity
        border.color: Qt.rgba(0, 1, 1, 0.3)
        border.width: 1
        clip: true
        z: 1

        // Corner decorations
        Rectangle { width: 5; height: 5; color: neonCyan; z: 10; anchors.top: parent.top;    anchors.left:  parent.left  }
        Rectangle { width: 5; height: 5; color: neonCyan; z: 10; anchors.top: parent.top;    anchors.right: parent.right }
        Rectangle { width: 5; height: 5; color: neonCyan; z: 10; anchors.bottom: parent.bottom; anchors.left:  parent.left  }
        Rectangle { width: 5; height: 5; color: neonCyan; z: 10; anchors.bottom: parent.bottom; anchors.right: parent.right }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 10
            spacing: 8
            z: 2

            // ── TITLE BAR ──────────────────────────────────────────
            RowLayout {
                Layout.fillWidth: true
                spacing: 5

                // MOVE label
                Rectangle {
                    width: moveLbl.implicitWidth + 10; height: 20
                    color: "transparent"
                    border.color: Qt.rgba(0, 1, 1, 0.4); border.width: 1
                    z: 10
                    Text {
                        id: moveLbl; anchors.centerIn: parent
                        text: "CTRL+MOVE"; font.family: "Orbitron"; font.pixelSize: 8; color: neonCyan
                    }
                    // MOVE just shows label — actual drag is handled by windowMoveHandler above
                }

                Text {
                    text: "◈ TUXILE" + (cursorVisible ? "_" : " ")
                    font.family: "Orbitron"; font.pixelSize: 11; font.bold: true; color: neonCyan
                }

                Item { Layout.fillWidth: true }

                // A- button
                Rectangle {
                    id: aMinusBtn
                    width: 28; height: 20
                    color: "transparent"
                    border.color: Qt.rgba(0, 1, 1, 0.4); border.width: 1
                    z: 10
                    Text {
                        anchors.centerIn: parent
                        text: "A-"; font.family: "Orbitron"; font.pixelSize: 8; color: neonCyan
                    }
                    MouseArea {
                        anchors.fill: parent
                        z: 10
                        onClicked: bridge.decreaseFontSize()
                    }
                }

                // A+ button
                Rectangle {
                    id: aPlusBtn
                    width: 28; height: 20
                    color: "transparent"
                    border.color: Qt.rgba(0, 1, 1, 0.4); border.width: 1
                    z: 10
                    Text {
                        anchors.centerIn: parent
                        text: "A+"; font.family: "Orbitron"; font.pixelSize: 8; color: neonCyan
                    }
                    MouseArea {
                        anchors.fill: parent
                        z: 10
                        onClicked: bridge.increaseFontSize()
                    }
                }

                // R button
                Rectangle {
                    id: rBtn
                    width: 22; height: 20
                    color: "transparent"
                    border.color: Qt.rgba(1, 0.8, 0, 0.5); border.width: 1
                    z: 10
                    Text {
                        anchors.centerIn: parent
                        text: "R"; font.family: "Orbitron"; font.pixelSize: 8; color: neonYellow
                    }
                    MouseArea {
                        anchors.fill: parent
                        z: 10
                        onClicked: bridge.resetProgress()
                    }
                }

                // Click-through toggle
                Rectangle {
                    id: clickThroughBtn
                    width: 22; height: 20
                    color: "transparent"
                    border.color: bridge.clickThrough ? dangerRed : neonCyan; border.width: 1
                    z: 10
                    Text {
                        anchors.centerIn: parent
                        text: bridge.clickThrough ? "L" : "U"
                        font.family: "Orbitron"; font.pixelSize: 8; color: bridge.clickThrough ? dangerRed : neonCyan
                    }
                    MouseArea {
                        anchors.fill: parent
                        z: 10
                        onClicked: bridge.toggleClickThrough()
                        ToolTip.visible: containsMouse
                        ToolTip.text: bridge.clickThrough ? "Click-through ON (Locked)" : "Click-through OFF (Unlocked)"
                    }
                }

                // X button
                Rectangle {
                    id: xBtn
                    width: 22; height: 20
                    color: "transparent"
                    border.color: Qt.rgba(1, 0.27, 0.4, 0.5); border.width: 1
                    z: 10
                    Text {
                        anchors.centerIn: parent
                        text: "X"; font.family: "Orbitron"; font.pixelSize: 8; color: dangerRed
                    }
                    MouseArea {
                        anchors.fill: parent
                        z: 10
                        onClicked: Qt.quit()
                    }
                }
            }

            // Separator
            Rectangle {
                Layout.fillWidth: true; height: 1
                color: Qt.rgba(0, 1, 0.78, 0.15)
            }

            // ── ACT BADGE ──────────────────────────────────────────
            Rectangle {
                Layout.alignment: Qt.AlignLeft
                width: actText.implicitWidth + 16; height: 22
                color: "transparent"
                border.color: neonPurple; border.width: 1
                Text {
                    id: actText; anchors.centerIn: parent
                    text: bridge.actTitle.toUpperCase()
                    color: neonPurple; font.family: "Share Tech Mono"; font.pixelSize: 10
                }
            }

            // ── STEP CONTENT ───────────────────────────────────────
            Item {
                Layout.fillWidth: true
                Layout.fillHeight: true

                ScrollView {
                    anchors.fill: parent
                    contentWidth: availableWidth
                    clip: true

                    Column {
                        id: stepColumn
                        width: parent.width
                        spacing: 6

                        Repeater {
                            model: bridge.substeps
                            delegate: Item {
                                width: stepColumn.width
                                height: Math.max(20, stepText.implicitHeight + 4)

                                RowLayout {
                                    anchors.fill: parent
                                    spacing: 8

                                    Rectangle {
                                        width: 5; height: 5; rotation: 45
                                        color: modelData.isCompleted ? mutedText : neonCyan
                                        opacity: modelData.isCompleted ? 0.4 : 1.0
                                        Layout.alignment: Qt.AlignTop
                                        Layout.topMargin: 5
                                    }

                                    Text {
                                        id: stepText
                                        Layout.fillWidth: true
                                        // Strip any leftover [ICON:...] tags that Qt6 can't render
                                        text: modelData.text.replace(/\[ICON:[^\]]+\]/g, "")
                                        color: modelData.isCompleted ? mutedText : primaryText
                                        opacity: modelData.isCompleted ? 0.4 : 1.0
                                        font.family: "Share Tech Mono"
                                        font.pixelSize: bridge.baseFontSize
                                        wrapMode: Text.WordWrap
                                        textFormat: Text.RichText

                                        MouseArea {
                                            anchors.fill: parent
                                            z: 5
                                            onClicked: bridge.onSubstepClicked(index)
                                        }
                                    }
                                }
                            }
                        }

                        opacity: 1.0
                        Behavior on opacity { NumberAnimation { duration: 200 } }
                    }
                }

                Connections {
                    target: bridge
                    function onCurrentStepIndexChanged() {
                        stepColumn.opacity = 0
                        fadeTimer.start()
                    }
                }
                Timer {
                    id: fadeTimer; interval: 250
                    onTriggered: stepColumn.opacity = 1.0
                }
            }

            // ── NAVIGATION ─────────────────────────────────────────
            RowLayout {
                Layout.fillWidth: true
                spacing: 4

                // PREV
                Rectangle {
                    width: prevLbl.implicitWidth + 16; height: 22
                    color: "transparent"
                    border.color: Qt.rgba(0, 1, 1, 0.4); border.width: 1
                    opacity: bridge.currentStepIndex > 0 ? 1.0 : 0.3
                    z: 10
                    Text {
                        id: prevLbl; anchors.centerIn: parent
                        text: "◂ PREV"; font.family: "Orbitron"; font.pixelSize: 9; color: neonCyan
                    }
                    MouseArea {
                        anchors.fill: parent; z: 10
                        enabled: bridge.currentStepIndex > 0
                        onClicked: bridge.onPrevStep()
                    }
                }

                Item { Layout.fillWidth: true }

                Text {
                    text: "STEP " + (bridge.currentStepIndex + 1) + " / " + bridge.totalSteps
                    color: mutedText; font.family: "Share Tech Mono"; font.pixelSize: 10
                }

                Item { Layout.fillWidth: true }

                // NEXT
                Rectangle {
                    width: nextLbl.implicitWidth + 16; height: 22
                    color: "transparent"
                    border.color: Qt.rgba(0, 1, 1, 0.4); border.width: 1
                    opacity: bridge.currentStepIndex < bridge.totalSteps - 1 ? 1.0 : 0.3
                    z: 10
                    Text {
                        id: nextLbl; anchors.centerIn: parent
                        text: "NEXT ▸"; font.family: "Orbitron"; font.pixelSize: 9; color: neonCyan
                    }
                    MouseArea {
                        anchors.fill: parent; z: 10
                        enabled: bridge.currentStepIndex < bridge.totalSteps - 1
                        onClicked: bridge.onNextStep()
                    }
                }
            }

            // ── PROGRESS BAR ───────────────────────────────────────
            Rectangle {
                Layout.fillWidth: true; height: 3
                color: Qt.rgba(1, 1, 1, 0.05)
                Rectangle {
                    height: parent.height
                    width: parent.width * (bridge.totalSteps > 1
                           ? (bridge.currentStepIndex / (bridge.totalSteps - 1)) : 0)
                    opacity: glowOpacity
                    gradient: Gradient {
                        orientation: Gradient.Horizontal
                        GradientStop { position: 0.0; color: neonPurple }
                        GradientStop { position: 1.0; color: neonCyan }
                    }
                    Behavior on width { NumberAnimation { duration: 300; easing.type: Easing.OutQuad } }
                }
            }

        } // ColumnLayout
    } // mainContainer
}
