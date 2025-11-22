
//  Copyright (c) 2003-2025 Movella Technologies B.V. or subsidiaries worldwide.
//  All rights reserved.
//  
//  Redistribution and use in source and binary forms, with or without modification,
//  are permitted provided that the following conditions are met:
//  
//  1.	Redistributions of source code must retain the above copyright notice,
//  	this list of conditions, and the following disclaimer.
//  
//  2.	Redistributions in binary form must reproduce the above copyright notice,
//  	this list of conditions, and the following disclaimer in the documentation
//  	and/or other materials provided with the distribution.
//  
//  3.	Neither the names of the copyright holders nor the names of their contributors
//  	may be used to endorse or promote products derived from this software without
//  	specific prior written permission.
//  
//  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
//  EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
//  MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
//  THE COPYRIGHT HOLDERS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
//  SPECIAL, EXEMPLARY OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT 
//  OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
//  HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY OR
//  TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
//  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.THE LAWS OF THE NETHERLANDS 
//  SHALL BE EXCLUSIVELY APPLICABLE AND ANY DISPUTES SHALL BE FINALLY SETTLED UNDER THE RULES 
//  OF ARBITRATION OF THE INTERNATIONAL CHAMBER OF COMMERCE IN THE HAGUE BY ONE OR MORE 
//  ARBITRATORS APPOINTED IN ACCORDANCE WITH SAID RULES.
//  

//------------------------------------------------------------------------------
// Awinda monitor main window
//------------------------------------------------------------------------------

#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <stdexcept>
#include <map>

#include <QMainWindow>
#include <QListWidgetItem>
#include <QTimer>
#include <QThread>
#include <QImage>
#include <QTime>
#include <QList>
#include <QSharedPointer>
#include <QElapsedTimer>

#include "myxda.h"
#include "connectedmtwdata.h"

namespace Ui {
    class MainWindow;
}

typedef enum {
	DETECTING,
    CONNECTING,
    CONNECTED,
    ENABLED,
	OPERATIONAL,
    AWAIT_MEASUREMENT_START,
    MEASURING,
	AWAIT_RECORDING_START,
    RECORDING,
    FLUSHING
} States;


class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = 0);
    ~MainWindow();

private slots:
#if 0 //TODO PORT
    void onRecordingStopped(XsensDeviceId mainDeviceId);
#endif

    // -- GUI slots --
    void toggleRadioEnabled();
	void setRadioChannel(int channel);
    void toggleMeasurement();
    void toggleRecording();
    void clearLogWindow();
    void clearConnectedMtwDataLabels();
	void requestBatteryLevels();

	// -- XDA event handlers --
	void handleWirelessMasterDetected(XsPortInfo);
	void handleDockedMtwDetected(XsPortInfo);
	void handleMtwUndocked(XsPortInfo);
	void handleOpenPortSuccessful(XsPortInfo const &);
	void handleOpenPortFailed(XsPortInfo const &);
	void handleMeasurementStarted(XsDeviceId);
    void handleMeasurementStopped(XsDeviceId);
    void handleError(XsDeviceId, XsResultValue);
	void handleWaitingForRecordingStart(XsDeviceId);
	void handleRecordingStarted(XsDeviceId);
	void handleProgressUpdate(XsDeviceId, int, int, QString);

	// -- XsCallback event handlers --
	void handleMtwWireless(XsDeviceId);
	void handleMtwDisconnected(XsDeviceId);
	void handleDataAvailable(XsDeviceId, XsDataPacket);
	void handleBatteryLevelChanged(XsDeviceId, int);

signals:
    void closeLogFile();

private:	
    Ui::MainWindow* m_ui;

    void setWidgetsStates();
    void log(const QString& message);
    void displayMtwData(ConnectedMTwData* mtwData);
	void clearMeasuringMtws();

	States m_state;

	// XDA
    MyXda* m_myXda;
	MyWirelessMasterCallback m_myWirelessMasterCallback;    
	XsDevicePtr m_myWirelessMasterDevice;
	std::map<XsDevicePtr, QSharedPointer<MyMtwCallback> > m_measuringMtws;
	std::map<XsDevicePtr, QSharedPointer<MyMtwCallback> >::iterator m_nextBatteryRequest;

	// QT
	QTimer* m_portScanTimer;
	QTimer* m_batteryLevelRequestTimer;
	QThread* m_xdaThread;
	QElapsedTimer m_timestamp;

	mutable QMutex m_mutex;
};


#endif // MAINWINDOW_H
