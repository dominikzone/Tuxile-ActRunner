import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window

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
        height: 32
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

            // Character profile button
            Rectangle {
                id: charBtn
                height: 20; radius: 2
                width: charBtnLabel.implicitWidth + 16
                color: charBtnHover.containsMouse ? Qt.rgba(0, 1, 1, 0.1) : Qt.rgba(0, 1, 1, 0.05)
                border.color: Qt.rgba(0, 1, 1, 0.3); border.width: 1
                Layout.alignment: Qt.AlignVCenter

                Text {
                    id: charBtnLabel
                    anchors.centerIn: parent
                    text: "⚔ " + (bridge ? bridge.activeCharacterName : "—")
                    color: neonCyan
                    font.family: "Barlow Condensed"; font.pixelSize: 10; font.weight: Font.DemiBold
                }

                MouseArea {
                    id: charBtnHover
                    anchors.fill: parent
                    hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                    onPressed: bridge.profileModalOpen ? bridge.closeProfileModal() : bridge.openProfileModal()
                }
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
                width: tbAMinus.implicitWidth + 14; height: 20; radius: 2; color: "transparent"
                border.color: Qt.rgba(0, 1, 1, 0.15); border.width: 1
                Layout.alignment: Qt.AlignVCenter
                Text { id: tbAMinus; anchors.centerIn: parent; text: "A-"; color: mutedText; font.family: "Barlow Condensed"; font.pixelSize: 10; font.weight: Font.DemiBold }
                MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onPressed: (m) => { if (m.modifiers & Qt.ControlModifier) bridge.decreaseFontSize() } }
            }

            // A+
            Rectangle {
                width: tbAPlus.implicitWidth + 14; height: 20; radius: 2; color: "transparent"
                border.color: Qt.rgba(0, 1, 1, 0.15); border.width: 1
                Layout.alignment: Qt.AlignVCenter
                Text { id: tbAPlus; anchors.centerIn: parent; text: "A+"; color: mutedText; font.family: "Barlow Condensed"; font.pixelSize: 10; font.weight: Font.DemiBold }
                MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onPressed: (m) => { if (m.modifiers & Qt.ControlModifier) bridge.increaseFontSize() } }
            }

            // R (reset)
            Rectangle {
                width: tbR.implicitWidth + 14; height: 20; radius: 2; color: "transparent"
                border.color: rHover.containsMouse ? Qt.rgba(1, 0.27, 0.4, 0.5) : Qt.rgba(0, 1, 1, 0.15); border.width: 1
                Layout.alignment: Qt.AlignVCenter
                Text { id: tbR; anchors.centerIn: parent; text: "R"; color: rHover.containsMouse ? dangerRed : mutedText; font.family: "Barlow Condensed"; font.pixelSize: 10; font.weight: Font.DemiBold }
                MouseArea { id: rHover; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onPressed: (m) => { if (m.modifiers & Qt.ControlModifier) bridge.resetProgress() } }
            }

            // ✕ (close)
            Rectangle {
                width: tbX.implicitWidth + 14; height: 20; radius: 2; color: "transparent"
                border.color: xHover.containsMouse ? Qt.rgba(1, 0.27, 0.4, 0.5) : Qt.rgba(0, 1, 1, 0.15); border.width: 1
                Layout.alignment: Qt.AlignVCenter
                Text { id: tbX; anchors.centerIn: parent; text: "✕"; color: xHover.containsMouse ? dangerRed : mutedText; font.family: "Barlow Condensed"; font.pixelSize: 10; font.weight: Font.DemiBold }
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

        // ── SIDEBAR (right, 36px) ─────────────────────────────────────
        Rectangle {
            id: sidebar
            anchors.top: parent.top; anchors.bottom: parent.bottom
            anchors.right: parent.right
            width: 36
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
                width: parent.width; height: 26
                Text { anchors.centerIn: parent; text: "▲"; color: neonCyan; font.pixelSize: 16 }
                MouseArea {
                    anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                    onPressed: (m) => { if (m.modifiers & Qt.ControlModifier) bridge.onPrevStep() }
                }
            }

            // ▼ button
            Item {
                id: sidebarNext
                anchors.bottom: parent.bottom
                width: parent.width; height: 26
                Text { anchors.centerIn: parent; text: "▼"; color: neonCyan; font.pixelSize: 16 }
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
                    font.family: "Barlow Condensed"; font.pixelSize: 8
                }
            }

            // Progress track (fills between ▲ and percentage label)
            Item {
                anchors.top: sidebarPrev.bottom
                anchors.bottom: sidebarPct.top
                width: parent.width

                Rectangle {
                    width: 5; radius: 2
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

                    Text {
                        visible: bridge && !bridge.stepRequirementMet
                        text: "⏳"
                        font.pixelSize: 9
                        color: neonYellow
                        leftPadding: 3
                    }

                    Item { Layout.fillWidth: true }

                    Text {
                        text: (bridge.currentActStepIndex + 1) + "/" + bridge.currentActTotalSteps
                        color: "#ffcc00"; font.family: "Barlow Condensed"; font.pixelSize: 8
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
                spacing: 6

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
                        height: bridge.baseFontSize + 10
                        clip: true

                        Row {
                            anchors.verticalCenter: parent.verticalCenter
                            spacing: 4

                            // Icon column
                            Text {
                                width: 16
                                anchors.verticalCenter: parent.verticalCenter
                                text: {
                                    var t = modelData.iconType
                                    if (t === "waypoint") return "🔵"
                                    if (t === "boss")     return "⚔"
                                    if (t === "quest")    return "❗"
                                    if (t === "item")     return "📦"
                                    if (t === "trial")    return "🏆"
                                    if (t === "town")     return "🏠"
                                    return "→"
                                }
                                color: neonCyan
                                font.pixelSize: bridge.baseFontSize
                                font.family: "Barlow Condensed"
                                font.weight: Font.DemiBold
                            }

                            // Text column
                            Text {
                                width: substepList.width - 20
                                anchors.verticalCenter: parent.verticalCenter
                                text: modelData.text
                                color: primaryText
                                opacity: 1.0
                                font.family: "Barlow Condensed"
                                font.pixelSize: bridge.baseFontSize
                                font.weight: Font.DemiBold
                                textFormat: Text.RichText
                                clip: true
                            }
                        }
                    }
                }
            }
        }
    }

    // ── PROFILE MODAL (separate OS window, child of root for id scope) ─
    Window {
    id: profileModal
    flags: Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
    color: "transparent"
    visible: bridge ? bridge.profileModalOpen : false
    width: 340
    height: modalBg.implicitHeight

    property string pendingDeleteName: ""
    property bool confirmVisible: false

    // Smart positioning: below main window if space, above otherwise
    x: Math.max(0, Math.min(root.x, Screen.desktopAvailableWidth - 340))
    y: {
        var mh = modalBg.implicitHeight
        var spaceBelow = Screen.desktopAvailableHeight - (root.y + root.height)
        if (spaceBelow >= mh + 4)
            return root.y + root.height + 4
        else
            return Math.max(0, root.y - mh - 4)
    }

    Rectangle {
        id: modalBg
        width: 340
        implicitHeight: modalCol.implicitHeight
        height: implicitHeight
        color: "#0d0d20"
        border.color: Qt.rgba(0, 1, 1, 0.3); border.width: 1
        radius: 6
        clip: true

        Column {
            id: modalCol
            width: 340

            // ── Header ──────────────────────────────────────────────
            Rectangle {
                width: parent.width; height: 32
                color: "#0a0a18"
                Rectangle {
                    anchors.bottom: parent.bottom
                    anchors.left: parent.left; anchors.right: parent.right
                    height: 1; color: Qt.rgba(0, 1, 1, 0.1)
                }
                RowLayout {
                    anchors.fill: parent; anchors.leftMargin: 10; anchors.rightMargin: 8
                    spacing: 6
                    Text {
                        text: "⚔ CHARACTER PROFILES"; color: "#00ffff"
                        font.family: "Orbitron"; font.pixelSize: 11; font.weight: Font.DemiBold
                        Layout.alignment: Qt.AlignVCenter
                    }
                    Item { Layout.fillWidth: true }
                    Rectangle {
                        height: 22; radius: 2
                        width: modalCloseLbl.implicitWidth + 16
                        color: modalCloseHover.containsMouse ? Qt.rgba(1, 0.27, 0.4, 0.15) : "transparent"
                        border.color: modalCloseHover.containsMouse ? Qt.rgba(1, 0.27, 0.4, 0.5) : Qt.rgba(0, 1, 1, 0.15)
                        border.width: 1
                        Layout.alignment: Qt.AlignVCenter
                        Text {
                            id: modalCloseLbl; anchors.centerIn: parent
                            text: "✕ close"
                            color: modalCloseHover.containsMouse ? "#ff4466" : "#4a6a5a"
                            font.family: "Barlow Condensed"; font.pixelSize: 11
                        }
                        MouseArea {
                            id: modalCloseHover; anchors.fill: parent
                            hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                            onPressed: bridge.closeProfileModal()
                        }
                    }
                }
            }

            // ── Character rows ───────────────────────────────────────
            Column {
                width: parent.width
                topPadding: 8; bottomPadding: 6; leftPadding: 10; rightPadding: 10
                spacing: 4

                Text {
                    text: "SELECT ACTIVE CHARACTER"; color: "#4a6a5a"
                    font.family: "Barlow Condensed"; font.pixelSize: 10; font.weight: Font.DemiBold
                    font.letterSpacing: 1
                    bottomPadding: 4
                }

                Repeater {
                    model: bridge ? bridge.characterList : []
                    delegate: Rectangle {
                        id: charRowRect
                        property bool rowHovered: false
                        width: 320; height: 42; radius: 3
                        color: modelData.isActive
                               ? Qt.rgba(0, 1, 1, 0.07)
                               : (rowHovered ? Qt.rgba(0, 1, 1, 0.04) : "transparent")
                        border.color: modelData.isActive
                                      ? Qt.rgba(0, 1, 1, 0.25)
                                      : (rowHovered ? Qt.rgba(0, 1, 1, 0.1) : "transparent")
                        border.width: 1

                        // Row click — declared first so RowLayout children render above it
                        MouseArea {
                            anchors.fill: parent; hoverEnabled: true
                            cursorShape: modelData.isActive ? Qt.ArrowCursor : Qt.PointingHandCursor
                            onContainsMouseChanged: charRowRect.rowHovered = containsMouse
                            onPressed: {
                                if (!modelData.isActive && !delItem.delHovered)
                                    bridge.switchCharacter(modelData.name)
                            }
                        }

                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 10; anchors.rightMargin: 8
                            spacing: 6

                            Column {
                                Layout.fillWidth: true
                                Layout.alignment: Qt.AlignVCenter
                                spacing: 3

                                Text {
                                    text: modelData.name
                                    color: modelData.isActive ? "#00ffff" : "#e8ffe8"
                                    font.family: "Barlow Condensed"; font.pixelSize: 13; font.weight: Font.Bold
                                    elide: Text.ElideRight
                                    width: parent.width
                                }

                                Row {
                                    spacing: 5

                                    Text {
                                        text: "ACT " + modelData.actNumber
                                        color: "#ffcc00"
                                        font.family: "Barlow Condensed"; font.pixelSize: 10; font.weight: Font.DemiBold
                                        anchors.verticalCenter: parent.verticalCenter
                                    }

                                    Rectangle {
                                        visible: modelData.isActive
                                        height: 12; radius: 2
                                        width: activeBadgeLbl.implicitWidth + 6
                                        color: "transparent"
                                        border.color: Qt.rgba(0, 1, 0.53, 0.3); border.width: 1
                                        anchors.verticalCenter: parent.verticalCenter
                                        Text {
                                            id: activeBadgeLbl; anchors.centerIn: parent
                                            text: "ACTIVE"
                                            color: "#00ff88"
                                            font.family: "Barlow Condensed"; font.pixelSize: 7; font.weight: Font.DemiBold
                                        }
                                    }
                                }
                            }

                            // Delete button
                            Item {
                                id: delItem
                                width: delLbl.implicitWidth + 12; height: 22
                                Layout.alignment: Qt.AlignVCenter
                                property bool delHovered: false
                                property bool canDelete: bridge && bridge.characterList.length > 1
                                opacity: bridge && bridge.characterList.length <= 1 ? 0.2 : 1.0

                                Rectangle {
                                    anchors.fill: parent; radius: 2
                                    color: "transparent"
                                    border.color: delItem.delHovered && delItem.canDelete
                                                  ? Qt.rgba(1, 0.27, 0.4, 0.5)
                                                  : Qt.rgba(0, 1, 1, 0.1)
                                    border.width: 1
                                }
                                Text {
                                    id: delLbl; anchors.centerIn: parent
                                    text: "✕"
                                    color: delItem.delHovered && delItem.canDelete ? "#ff4466" : "#4a6a5a"
                                    font.family: "Barlow Condensed"; font.pixelSize: 12
                                    leftPadding: 6; rightPadding: 6
                                }
                                MouseArea {
                                    z: 10
                                    anchors.fill: parent; hoverEnabled: true
                                    propagateComposedEvents: false
                                    enabled: delItem.canDelete
                                    cursorShape: delItem.canDelete ? Qt.PointingHandCursor : Qt.ArrowCursor
                                    onContainsMouseChanged: delItem.delHovered = containsMouse
                                    onPressed: (m) => {
                                        m.accepted = true
                                        if (delItem.canDelete) {
                                            profileModal.pendingDeleteName = modelData.name
                                            profileModal.confirmVisible = true
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // ── Divider ──────────────────────────────────────────────
            Rectangle { width: parent.width; height: 1; color: Qt.rgba(0, 1, 1, 0.08) }

            // ── Add new character ────────────────────────────────────
            Column {
                width: parent.width
                topPadding: 8; bottomPadding: 10; leftPadding: 10; rightPadding: 10
                spacing: 6

                Text {
                    text: "ADD NEW CHARACTER"; color: "#4a6a5a"
                    font.family: "Barlow Condensed"; font.pixelSize: 10; font.weight: Font.DemiBold
                    font.letterSpacing: 1
                }

                RowLayout {
                    width: 320; spacing: 6

                    Rectangle {
                        Layout.fillWidth: true; height: 32; radius: 3
                        color: "#06060f"
                        border.color: modalInput.activeFocus ? Qt.rgba(0, 1, 1, 0.5) : Qt.rgba(0, 1, 1, 0.2)
                        border.width: 1
                        TextInput {
                            id: modalInput
                            anchors.fill: parent; anchors.leftMargin: 10; anchors.rightMargin: 10
                            color: "#e8ffe8"; verticalAlignment: TextInput.AlignVCenter; clip: true
                            font.family: "Barlow Condensed"; font.pixelSize: 12; font.weight: Font.DemiBold
                            selectionColor: Qt.rgba(0, 1, 1, 0.3)
                            Text {
                                anchors.fill: parent; verticalAlignment: Text.AlignVCenter
                                text: "Character name..."; color: "#4a6a5a"; font: parent.font
                                visible: parent.text.length === 0
                            }
                            Keys.onReturnPressed: {
                                var t = text.trim()
                                if (t !== "") { bridge.addCharacter(t); text = "" }
                            }
                            Keys.onEscapePressed: { text = ""; bridge.closeProfileModal() }
                        }
                    }

                    Rectangle {
                        width: addBtnLbl.implicitWidth + 24; height: 32; radius: 3
                        color: "transparent"
                        border.color: addBtnHover.containsMouse ? Qt.rgba(0, 1, 0.53, 0.6) : Qt.rgba(0, 1, 0.53, 0.3)
                        border.width: 1
                        Text {
                            id: addBtnLbl; anchors.centerIn: parent
                            text: "＋ ADD"
                            color: "#00ff88"
                            font.family: "Barlow Condensed"; font.pixelSize: 11; font.weight: Font.DemiBold
                        }
                        MouseArea {
                            id: addBtnHover; anchors.fill: parent
                            hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                            onPressed: {
                                var t = modalInput.text.trim()
                                if (t !== "") { bridge.addCharacter(t); modalInput.text = "" }
                            }
                        }
                    }
                }
            }

            // ── Global note ──────────────────────────────────────────
            Rectangle {
                width: parent.width; height: globalNoteTxt.implicitHeight + 16
                color: Qt.rgba(0, 0, 0, 0.2)
                Rectangle {
                    anchors.top: parent.top; anchors.left: parent.left; anchors.right: parent.right
                    height: 1; color: Qt.rgba(0, 1, 1, 0.06)
                }
                Text {
                    id: globalNoteTxt
                    anchors.left: parent.left; anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.leftMargin: 10; anchors.rightMargin: 10
                    text: "⚙ Font size and window size are <span style='color:#ffcc00'>global</span> — shared across all characters"
                    color: "#4a6a5a"
                    font.family: "Barlow Condensed"; font.pixelSize: 10
                    wrapMode: Text.Wrap; textFormat: Text.RichText
                }
            }
        }
        // Confirmation overlay
        Rectangle {
            anchors.fill: parent
            visible: profileModal.confirmVisible
            z: 10
            color: Qt.rgba(6/255, 6/255, 15/255, 0.9)
            radius: 6

            Rectangle {
                id: confirmBox
                anchors.centerIn: parent
                width: 260
                height: confirmCol.implicitHeight + 32
                color: "#0d0d20"
                border.color: Qt.rgba(1, 0.27, 0.4, 0.4); border.width: 1
                radius: 6

                Column {
                    id: confirmCol
                    anchors {
                        top: parent.top; left: parent.left; right: parent.right
                        topMargin: 16; leftMargin: 16; rightMargin: 16
                    }
                    spacing: 8

                    Text {
                        text: "⚠ DELETE PROFILE?"
                        color: "#ff4466"
                        font.family: "Orbitron"; font.pixelSize: 10; font.weight: Font.DemiBold
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Rectangle { width: parent.width; height: 1; color: Qt.rgba(1, 0.27, 0.4, 0.2) }

                    Text {
                        text: profileModal.pendingDeleteName
                        color: "#e8ffe8"
                        font.family: "Barlow Condensed"; font.pixelSize: 13; font.weight: Font.Bold
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Text {
                        text: "This will permanently\ndelete all progress."
                        color: "#4a6a5a"
                        font.family: "Barlow Condensed"; font.pixelSize: 10
                        horizontalAlignment: Text.AlignHCenter
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Rectangle { width: parent.width; height: 1; color: Qt.rgba(1, 0.27, 0.4, 0.2) }

                    Row {
                        width: parent.width
                        spacing: 8

                        Rectangle {
                            width: (parent.width - 8) / 2; height: 28; radius: 3
                            color: yesHover.containsMouse ? Qt.rgba(1, 0.27, 0.4, 0.15) : Qt.rgba(1, 0.27, 0.4, 0.08)
                            border.color: Qt.rgba(1, 0.27, 0.4, 0.4); border.width: 1
                            Text {
                                anchors.centerIn: parent
                                text: "YES, DELETE"
                                color: "#ff4466"
                                font.family: "Barlow Condensed"; font.pixelSize: 11; font.weight: Font.DemiBold
                            }
                            MouseArea {
                                id: yesHover
                                anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                                onPressed: {
                                    bridge.deleteCharacter(profileModal.pendingDeleteName)
                                    profileModal.pendingDeleteName = ""
                                    profileModal.confirmVisible = false
                                    bridge.closeProfileModal()
                                }
                            }
                        }

                        Rectangle {
                            width: (parent.width - 8) / 2; height: 28; radius: 3
                            color: "transparent"
                            border.color: Qt.rgba(1, 1, 1, 0.1); border.width: 1
                            Text {
                                anchors.centerIn: parent
                                text: "CANCEL"
                                color: cancelHover.containsMouse ? "#e8ffe8" : "#4a6a5a"
                                font.family: "Barlow Condensed"; font.pixelSize: 11; font.weight: Font.DemiBold
                            }
                            MouseArea {
                                id: cancelHover
                                anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                                onPressed: {
                                    profileModal.pendingDeleteName = ""
                                    profileModal.confirmVisible = false
                                }
                            }
                        }
                    }
                }
            }
        }
    }
} // profileModal

    // ── UPDATE POPUP ──────────────────────────────────────────────────
    Window {
        id: updatePopup
        flags: Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        color: "transparent"
        visible: bridge ? bridge.showUpdatePopup : false
        width: 360
        height: updateContent.implicitHeight

        x: root.x + (root.width  - width)  / 2
        y: Math.max(0, root.y + (root.height - height) / 2)

        Connections {
            target: root
            function onXChanged() {
                updatePopup.x = root.x + (root.width - updatePopup.width) / 2
            }
            function onYChanged() {
                updatePopup.y = Math.max(0,
                    root.y + (root.height - updatePopup.height) / 2)
            }
        }

        Rectangle {
            id: updateContent
            width: 360
            implicitHeight: updateCol.implicitHeight
            height: implicitHeight
            color: "#0d0d20"
            border.color: Qt.rgba(0, 1, 1, 0.3); border.width: 1
            radius: 6

            Column {
                id: updateCol
                width: 360
                spacing: 0

                // Header
                Rectangle {
                    width: parent.width; height: 32
                    color: "#0a0a18"
                    radius: 6
                    Rectangle {
                        anchors.bottom: parent.bottom
                        width: parent.width; height: 16
                        color: "#0a0a18"
                    }
                    Rectangle {
                        anchors.bottom: parent.bottom
                        anchors.left: parent.left; anchors.right: parent.right
                        height: 1; color: Qt.rgba(0, 1, 1, 0.08)
                    }
                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.left: parent.left; anchors.leftMargin: 10
                        text: "⬆ NEW VERSION AVAILABLE"
                        color: neonYellow
                        font.family: "Orbitron"; font.pixelSize: 10; font.weight: Font.DemiBold
                    }
                }

                // Version line
                Item {
                    width: parent.width; height: 36
                    Row {
                        anchors.centerIn: parent
                        spacing: 8
                        Text {
                            text: "v" + (bridge ? bridge.updateCurrent : "")
                            color: mutedText
                            font.family: "Barlow Condensed"; font.pixelSize: 13; font.weight: Font.DemiBold
                        }
                        Text {
                            text: "→"; color: neonYellow
                            font.family: "Barlow Condensed"; font.pixelSize: 13
                        }
                        Text {
                            text: "v" + (bridge ? bridge.updateLatest : "")
                            color: neonGreen
                            font.family: "Barlow Condensed"; font.pixelSize: 13; font.weight: Font.DemiBold
                        }
                    }
                }

                Rectangle { width: parent.width; height: 1; color: Qt.rgba(0, 1, 1, 0.08) }

                // Changelog
                Column {
                    width: parent.width
                    topPadding: 10; bottomPadding: 10; leftPadding: 10; rightPadding: 10
                    spacing: 6

                    Text {
                        text: "WHAT'S NEW"
                        color: mutedText
                        font.family: "Barlow Condensed"; font.pixelSize: 10
                        font.weight: Font.DemiBold; font.letterSpacing: 1
                    }
                    Text {
                        width: parent.width - 20
                        text: bridge ? bridge.updateChangelog : ""
                        color: primaryText
                        font.family: "Barlow Condensed"; font.pixelSize: 12; font.weight: Font.DemiBold
                        wrapMode: Text.WordWrap
                        lineHeight: 1.6
                    }
                }

                Rectangle { width: parent.width; height: 1; color: Qt.rgba(0, 1, 1, 0.08) }

                // Buttons
                Item {
                    width: parent.width; height: 48
                    Row {
                        anchors.centerIn: parent
                        spacing: 10

                        // YES button
                        Rectangle {
                            width: yesUpdateText.implicitWidth + 24; height: 30; radius: 3
                            color: yesUpdateHover.containsMouse
                                   ? Qt.rgba(0, 1, 0.53, 0.15) : Qt.rgba(0, 1, 0.53, 0.08)
                            border.color: Qt.rgba(0, 1, 0.53, 0.4); border.width: 1
                            Text {
                                id: yesUpdateText; anchors.centerIn: parent
                                text: "✓ YES, OPEN GITHUB"; color: neonGreen
                                font.family: "Barlow Condensed"; font.pixelSize: 11; font.weight: Font.DemiBold
                            }
                            MouseArea {
                                id: yesUpdateHover; anchors.fill: parent
                                hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                                onClicked: bridge.acceptUpdate()
                            }
                        }

                        // NO button
                        Rectangle {
                            id: noUpdateRect
                            width: noUpdateText.implicitWidth + 24; height: 30; radius: 3
                            color: "transparent"
                            border.color: noUpdateHover.containsMouse
                                          ? Qt.rgba(1, 1, 1, 0.25) : Qt.rgba(1, 1, 1, 0.1)
                            border.width: 1
                            Text {
                                id: noUpdateText; anchors.centerIn: parent
                                text: "✕ NOT NOW"
                                color: noUpdateHover.containsMouse ? primaryText : mutedText
                                font.family: "Barlow Condensed"; font.pixelSize: 11; font.weight: Font.DemiBold
                            }
                            MouseArea {
                                id: noUpdateHover; anchors.fill: parent
                                hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                                onClicked: bridge.dismissUpdate()
                            }
                        }
                    }
                }

                // Note
                Rectangle {
                    width: parent.width
                    height: updateNoteText.implicitHeight + 12
                    color: Qt.rgba(0, 0, 0, 0.2)
                    radius: 6
                    Rectangle {
                        anchors.top: parent.top
                        width: parent.width; height: 8
                        color: Qt.rgba(0, 0, 0, 0.2)
                    }
                    Text {
                        id: updateNoteText
                        anchors.centerIn: parent
                        width: parent.width - 20
                        text: "Clicking YES opens GitHub in your browser.\n" +
                              "Your profiles and progress are never affected by updates."
                        color: mutedText
                        font.family: "Barlow Condensed"; font.pixelSize: 9
                        wrapMode: Text.WordWrap
                        horizontalAlignment: Text.AlignHCenter
                        lineHeight: 1.5
                    }
                }
            }
        }
    } // updatePopup

} // Window (root)
