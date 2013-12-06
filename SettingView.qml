import QtQuick 2.1
import QtGraphicalEffects 1.0
import QtQuick.Window 2.1
import QtQuick.Layouts 1.0
import "./widgets"

Item {
    id: window
    
    property color bgColor: "#232323"
    property color fgColor: "#FFFFFF"
    property color contentBgColor: "#FFFFFF"

    property int frameRadius: 3
    property int shadowRadius: 10
    property int expandHeight: 100
    
    Component.onCompleted: {
        windowView.width = 250
        windowView.height = 350
        windowView.x = (screenWidth - windowView.width) / 2
        windowView.y = (screenHeight - windowView.height) / 2
    }
    
    Rectangle {
        id: frame
        anchors.centerIn: parent
        color: "#232323"
        radius: frameRadius
        border.width: 1
        border.color: Qt.rgba(1, 1, 1, 0.3)
        width: window.width - (shadowRadius + frameRadius) * 2
        height: window.height - (shadowRadius + frameRadius) * 2
        
        Item {
            anchors.top: parent.top
            anchors.right: parent.right
            width: closeImage.width
            height: closeImage.height
            
            Rectangle {
                id: closeBackground
                anchors.fill: parent
                anchors.topMargin: 3
                anchors.rightMargin: 3
                anchors.bottomMargin: 1
                anchors.leftMargin: 1
                color: Qt.rgba(0, 0, 0, 0)
            }
            
            Image {
                id: closeImage
                source: "image/window_close.png"
            }
            
            MouseArea {
                anchors.fill: parent
                hoverEnabled: true
                
                onEntered: {
                    closeBackground.color = Qt.rgba(1, 1, 1, 0.3)
                }
                
                onExited: {
                    closeBackground.color = Qt.rgba(1, 1, 1, 0)
                }
                
                onClicked: {
                    windowView.hide()
                }
            }
        }
        
        Text {
            id: name
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            height: paintedHeight + 40
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
            text: "深度翻译设置"
            color: "#fff"
			font { pixelSize: 20 }
            
            DragArea {
                anchors.fill: parent
                window: windowView
            }
        }
            
        Column {
            id: content
            anchors.top: name.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.leftMargin: 1
            anchors.rightMargin: 1
            
            property variant expandId: undefined
            property variant expandValue: undefined
            property bool changeLock: false
            
            signal turnOff(variant id)
            
            onExpandIdChanged: {
                if (content.expandId != undefined) {
                    for (var i = 0; i < content.children.length; i++) {
                        if (content.children[i] != content.expandId) {
                            content.children[i].expanded = false
                        }
                    }
                }
                
                //content.expandId = undefined
            }
            
            DBaseExpand {
                id: sourceExpand
	            expanded: false

                onExpandedChanged: {
                    header.item.checked = expanded
                }
                
                header.sourceComponent: DSwitcherButtonHeader {
                    text: "源语言"
                    width: parent.width
                    Component.onCompleted: {
                        checked = sourceExpand.expanded
                    }
                    onClicked: {
                        sourceExpand.expanded = checked
                        if (checked) {
                            content.expandId = sourceExpand
                        }
                    }
                }
                
                content.sourceComponent: Rectangle {
                    width: parent.width
                    height: expandHeight
                }
            }

            DBaseExpand {
                id: targetExpand
	            expanded: false

                onExpandedChanged: {
                    header.item.checked = expanded
                }
                
                header.sourceComponent: DSwitcherButtonHeader {
                    text: "目标语言"
                    width: parent.width
                    Component.onCompleted: {
                        checked = targetExpand.expanded
                    }
                    onClicked: {
                        targetExpand.expanded = checked
                        if (checked) {
                            content.expandId = targetExpand
                        }
                    }
                }
                
                content.sourceComponent: Rectangle {
                    width: parent.width
                    height: expandHeight
                }
            }
            
            DBaseExpand {
                id: wordExpand
	            expanded: false

                onExpandedChanged: {
                    header.item.checked = expanded
                }
                
                header.sourceComponent: DSwitcherButtonHeader {
                    text: "单词翻译"
                    width: parent.width
                    Component.onCompleted: {
                        checked = wordExpand.expanded
                    }
                    onClicked: {
                        wordExpand.expanded = checked
                        if (checked) {
                            content.expandId = wordExpand
                        }
                    }
                }
                
                content.sourceComponent: Rectangle {
                    width: parent.width
                    height: expandHeight
                }
            }

            DBaseExpand {
                id: wordsExpand
	            expanded: false

                onExpandedChanged: {
                    header.item.checked = expanded
                }
                
                header.sourceComponent: DSwitcherButtonHeader {
                    text: "长句翻译"
                    width: parent.width

                    Component.onCompleted: {
                        checked = wordsExpand.expanded
                    }

                    onClicked: {
                        wordsExpand.expanded = checked
                        if (checked) {
                            content.expandId = wordsExpand
                        }
                    }
                }
                
                content.sourceComponent: Rectangle {
                    width: parent.width
                    height: expandHeight
                }
            }
        }
            
        DTextButton {
            id: button
            text: "确定"
            anchors.bottom: parent.bottom
            anchors.right: parent.right
            anchors.margins: 5
            
            onClicked: {
                windowView.hide()
            }
        }
    }
    
    RectangularGlow {
        id: shadow
        anchors.fill: frame
        glowRadius: shadowRadius
        spread: 0.2
        color: Qt.rgba(0, 0, 0, 0.3)
        cornerRadius: frame.radius + shadowRadius
        visible: true
    }
}
