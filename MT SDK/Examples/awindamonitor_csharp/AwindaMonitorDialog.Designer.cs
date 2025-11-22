
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

﻿namespace AwindaMonitor
{
    partial class AwindaMonitorDialog
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(AwindaMonitorDialog));
            this.btnEnable = new System.Windows.Forms.Button();
            this.btnMeasure = new System.Windows.Forms.Button();
            this.btnRecord = new System.Windows.Forms.Button();
            this.labelDevId = new System.Windows.Forms.Label();
            this.labelDeviceId = new System.Windows.Forms.Label();
            this.comboBoxChannel = new System.Windows.Forms.ComboBox();
            this.labelChannel = new System.Windows.Forms.Label();
            this.groupBox1 = new System.Windows.Forms.GroupBox();
            this.labelStationId = new System.Windows.Forms.Label();
            this.progressBarFlushing = new System.Windows.Forms.ProgressBar();
            this.labelFlushing = new System.Windows.Forms.Label();
            this.textBoxFilename = new System.Windows.Forms.TextBox();
            this.labelFilename = new System.Windows.Forms.Label();
            this.comboBoxUpdateRate = new System.Windows.Forms.ComboBox();
            this.labelUpdateRate = new System.Windows.Forms.Label();
            this.dockedMtwListGroupBox = new System.Windows.Forms.GroupBox();
            this.dockedMtwList = new System.Windows.Forms.ListBox();
            this.connectedMtwListGroupBox = new System.Windows.Forms.GroupBox();
            this.connectedMtwList = new System.Windows.Forms.ListBox();
            this.checkBoxPitchToSelect = new System.Windows.Forms.CheckBox();
            this.groupBox4 = new System.Windows.Forms.GroupBox();
            this.logWindow = new System.Windows.Forms.RichTextBox();
            this.groupBox5 = new System.Windows.Forms.GroupBox();
            this.yawLabel = new System.Windows.Forms.Label();
            this.pitchLabel = new System.Windows.Forms.Label();
            this.rollLabel = new System.Windows.Forms.Label();
            this.effUpdateRateLabel = new System.Windows.Forms.Label();
            this.rssiLabel = new System.Windows.Forms.Label();
            this.batteryLevelLabel = new System.Windows.Forms.Label();
            this.label11 = new System.Windows.Forms.Label();
            this.label10 = new System.Windows.Forms.Label();
            this.label9 = new System.Windows.Forms.Label();
            this.label8 = new System.Windows.Forms.Label();
            this.label7 = new System.Windows.Forms.Label();
            this.label6 = new System.Windows.Forms.Label();
            this.groupBox6 = new System.Windows.Forms.GroupBox();
            this.pictureBoxStateDiagram = new System.Windows.Forms.PictureBox();
            this.pictureBox1 = new System.Windows.Forms.PictureBox();
            this.groupBox1.SuspendLayout();
            this.dockedMtwListGroupBox.SuspendLayout();
            this.connectedMtwListGroupBox.SuspendLayout();
            this.groupBox4.SuspendLayout();
            this.groupBox5.SuspendLayout();
            this.groupBox6.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.pictureBoxStateDiagram)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.pictureBox1)).BeginInit();
            this.SuspendLayout();
            // 
            // btnEnable
            // 
            this.btnEnable.Enabled = false;
            this.btnEnable.Location = new System.Drawing.Point(18, 76);
            this.btnEnable.Name = "btnEnable";
            this.btnEnable.Size = new System.Drawing.Size(144, 33);
            this.btnEnable.TabIndex = 4;
            this.btnEnable.Text = "Enable";
            this.btnEnable.UseVisualStyleBackColor = true;
            this.btnEnable.Click += new System.EventHandler(this.btnEnable_Click);
            // 
            // btnMeasure
            // 
            this.btnMeasure.Enabled = false;
            this.btnMeasure.Location = new System.Drawing.Point(18, 163);
            this.btnMeasure.Name = "btnMeasure";
            this.btnMeasure.Size = new System.Drawing.Size(144, 33);
            this.btnMeasure.TabIndex = 7;
            this.btnMeasure.Text = "Start Measuring";
            this.btnMeasure.UseVisualStyleBackColor = true;
            this.btnMeasure.Click += new System.EventHandler(this.btnMeasure_Click);
            // 
            // btnRecord
            // 
            this.btnRecord.Enabled = false;
            this.btnRecord.Location = new System.Drawing.Point(18, 249);
            this.btnRecord.Name = "btnRecord";
            this.btnRecord.Size = new System.Drawing.Size(144, 33);
            this.btnRecord.TabIndex = 8;
            this.btnRecord.Text = "Start Recording";
            this.btnRecord.UseVisualStyleBackColor = true;
            this.btnRecord.Click += new System.EventHandler(this.btnRecord_Click);
            // 
            // labelDevId
            // 
            this.labelDevId.AutoSize = true;
            this.labelDevId.Location = new System.Drawing.Point(15, 18);
            this.labelDevId.Name = "labelDevId";
            this.labelDevId.Size = new System.Drawing.Size(21, 13);
            this.labelDevId.TabIndex = 13;
            this.labelDevId.Text = "ID:";
            // 
            // labelDeviceId
            // 
            this.labelDeviceId.AutoSize = true;
            this.labelDeviceId.Location = new System.Drawing.Point(41, 30);
            this.labelDeviceId.Name = "labelDeviceId";
            this.labelDeviceId.Size = new System.Drawing.Size(0, 13);
            this.labelDeviceId.TabIndex = 14;
            // 
            // comboBoxChannel
            // 
            this.comboBoxChannel.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.comboBoxChannel.Enabled = false;
            this.comboBoxChannel.FormattingEnabled = true;
            this.comboBoxChannel.Items.AddRange(new object[] {
            "11",
            "12",
            "13",
            "14",
            "15",
            "16",
            "17",
            "18",
            "19",
            "20",
            "21",
            "22",
            "23",
            "24",
            "25"});
            this.comboBoxChannel.Location = new System.Drawing.Point(87, 40);
            this.comboBoxChannel.Name = "comboBoxChannel";
            this.comboBoxChannel.Size = new System.Drawing.Size(75, 21);
            this.comboBoxChannel.TabIndex = 15;
            // 
            // labelChannel
            // 
            this.labelChannel.AutoSize = true;
            this.labelChannel.Enabled = false;
            this.labelChannel.Location = new System.Drawing.Point(15, 43);
            this.labelChannel.Name = "labelChannel";
            this.labelChannel.Size = new System.Drawing.Size(49, 13);
            this.labelChannel.TabIndex = 16;
            this.labelChannel.Text = "Channel:";
            // 
            // groupBox1
            // 
            this.groupBox1.Controls.Add(this.labelStationId);
            this.groupBox1.Controls.Add(this.progressBarFlushing);
            this.groupBox1.Controls.Add(this.labelFlushing);
            this.groupBox1.Controls.Add(this.textBoxFilename);
            this.groupBox1.Controls.Add(this.labelFilename);
            this.groupBox1.Controls.Add(this.comboBoxUpdateRate);
            this.groupBox1.Controls.Add(this.labelUpdateRate);
            this.groupBox1.Controls.Add(this.labelDevId);
            this.groupBox1.Controls.Add(this.btnRecord);
            this.groupBox1.Controls.Add(this.comboBoxChannel);
            this.groupBox1.Controls.Add(this.labelChannel);
            this.groupBox1.Controls.Add(this.btnEnable);
            this.groupBox1.Controls.Add(this.btnMeasure);
            this.groupBox1.Location = new System.Drawing.Point(12, 12);
            this.groupBox1.Name = "groupBox1";
            this.groupBox1.Size = new System.Drawing.Size(176, 363);
            this.groupBox1.TabIndex = 17;
            this.groupBox1.TabStop = false;
            this.groupBox1.Text = "Wireless master properties:";
            // 
            // labelStationId
            // 
            this.labelStationId.AutoSize = true;
            this.labelStationId.Location = new System.Drawing.Point(87, 18);
            this.labelStationId.Name = "labelStationId";
            this.labelStationId.Size = new System.Drawing.Size(28, 13);
            this.labelStationId.TabIndex = 23;
            this.labelStationId.Text = "       ";
            // 
            // progressBarFlushing
            // 
            this.progressBarFlushing.Enabled = false;
            this.progressBarFlushing.Location = new System.Drawing.Point(76, 298);
            this.progressBarFlushing.Name = "progressBarFlushing";
            this.progressBarFlushing.Size = new System.Drawing.Size(85, 23);
            this.progressBarFlushing.TabIndex = 22;
            // 
            // labelFlushing
            // 
            this.labelFlushing.AutoSize = true;
            this.labelFlushing.Enabled = false;
            this.labelFlushing.Location = new System.Drawing.Point(21, 303);
            this.labelFlushing.Name = "labelFlushing";
            this.labelFlushing.Size = new System.Drawing.Size(49, 13);
            this.labelFlushing.TabIndex = 21;
            this.labelFlushing.Text = "Flushing:";
            // 
            // textBoxFilename
            // 
            this.textBoxFilename.Enabled = false;
            this.textBoxFilename.Location = new System.Drawing.Point(76, 213);
            this.textBoxFilename.Name = "textBoxFilename";
            this.textBoxFilename.Size = new System.Drawing.Size(86, 20);
            this.textBoxFilename.TabIndex = 20;
            this.textBoxFilename.Text = "logfile.mtb";
            // 
            // labelFilename
            // 
            this.labelFilename.AutoSize = true;
            this.labelFilename.Enabled = false;
            this.labelFilename.Location = new System.Drawing.Point(18, 217);
            this.labelFilename.Name = "labelFilename";
            this.labelFilename.Size = new System.Drawing.Size(52, 13);
            this.labelFilename.TabIndex = 19;
            this.labelFilename.Text = "Filename:";
            // 
            // comboBoxUpdateRate
            // 
            this.comboBoxUpdateRate.Enabled = false;
            this.comboBoxUpdateRate.FormattingEnabled = true;
            this.comboBoxUpdateRate.Location = new System.Drawing.Point(87, 125);
            this.comboBoxUpdateRate.Name = "comboBoxUpdateRate";
            this.comboBoxUpdateRate.Size = new System.Drawing.Size(75, 21);
            this.comboBoxUpdateRate.TabIndex = 18;
            // 
            // labelUpdateRate
            // 
            this.labelUpdateRate.AutoSize = true;
            this.labelUpdateRate.Enabled = false;
            this.labelUpdateRate.Location = new System.Drawing.Point(18, 129);
            this.labelUpdateRate.Name = "labelUpdateRate";
            this.labelUpdateRate.Size = new System.Drawing.Size(66, 13);
            this.labelUpdateRate.TabIndex = 17;
            this.labelUpdateRate.Text = "Update rate:";
            // 
            // dockedMtwListGroupBox
            // 
            this.dockedMtwListGroupBox.Controls.Add(this.dockedMtwList);
            this.dockedMtwListGroupBox.Location = new System.Drawing.Point(208, 12);
            this.dockedMtwListGroupBox.Name = "dockedMtwListGroupBox";
            this.dockedMtwListGroupBox.Size = new System.Drawing.Size(185, 160);
            this.dockedMtwListGroupBox.TabIndex = 18;
            this.dockedMtwListGroupBox.TabStop = false;
            this.dockedMtwListGroupBox.Text = "Docked Mtw list (0):";
            // 
            // dockedMtwList
            // 
            this.dockedMtwList.FormattingEnabled = true;
            this.dockedMtwList.Location = new System.Drawing.Point(7, 18);
            this.dockedMtwList.Name = "dockedMtwList";
            this.dockedMtwList.Size = new System.Drawing.Size(162, 134);
            this.dockedMtwList.TabIndex = 0;
            // 
            // connectedMtwListGroupBox
            // 
            this.connectedMtwListGroupBox.Controls.Add(this.connectedMtwList);
            this.connectedMtwListGroupBox.Controls.Add(this.checkBoxPitchToSelect);
            this.connectedMtwListGroupBox.Location = new System.Drawing.Point(208, 178);
            this.connectedMtwListGroupBox.Name = "connectedMtwListGroupBox";
            this.connectedMtwListGroupBox.Size = new System.Drawing.Size(185, 197);
            this.connectedMtwListGroupBox.TabIndex = 19;
            this.connectedMtwListGroupBox.TabStop = false;
            this.connectedMtwListGroupBox.Text = "Connected Mtw list (0):";
            // 
            // connectedMtwList
            // 
            this.connectedMtwList.FormattingEnabled = true;
            this.connectedMtwList.Location = new System.Drawing.Point(7, 23);
            this.connectedMtwList.Name = "connectedMtwList";
            this.connectedMtwList.Size = new System.Drawing.Size(162, 134);
            this.connectedMtwList.TabIndex = 9;
            // 
            // checkBoxPitchToSelect
            // 
            this.checkBoxPitchToSelect.AutoSize = true;
            this.checkBoxPitchToSelect.Location = new System.Drawing.Point(18, 166);
            this.checkBoxPitchToSelect.Name = "checkBoxPitchToSelect";
            this.checkBoxPitchToSelect.Size = new System.Drawing.Size(93, 17);
            this.checkBoxPitchToSelect.TabIndex = 8;
            this.checkBoxPitchToSelect.Text = "Pitch to select";
            this.checkBoxPitchToSelect.UseVisualStyleBackColor = true;
            // 
            // groupBox4
            // 
            this.groupBox4.Controls.Add(this.logWindow);
            this.groupBox4.Location = new System.Drawing.Point(400, 13);
            this.groupBox4.Name = "groupBox4";
            this.groupBox4.Size = new System.Drawing.Size(284, 159);
            this.groupBox4.TabIndex = 20;
            this.groupBox4.TabStop = false;
            this.groupBox4.Text = "What\'s going on:";
            // 
            // logWindow
            // 
            this.logWindow.Location = new System.Drawing.Point(12, 19);
            this.logWindow.Name = "logWindow";
            this.logWindow.Size = new System.Drawing.Size(258, 127);
            this.logWindow.TabIndex = 7;
            this.logWindow.Text = "";
            // 
            // groupBox5
            // 
            this.groupBox5.Controls.Add(this.yawLabel);
            this.groupBox5.Controls.Add(this.pitchLabel);
            this.groupBox5.Controls.Add(this.rollLabel);
            this.groupBox5.Controls.Add(this.effUpdateRateLabel);
            this.groupBox5.Controls.Add(this.rssiLabel);
            this.groupBox5.Controls.Add(this.batteryLevelLabel);
            this.groupBox5.Controls.Add(this.label11);
            this.groupBox5.Controls.Add(this.label10);
            this.groupBox5.Controls.Add(this.label9);
            this.groupBox5.Controls.Add(this.label8);
            this.groupBox5.Controls.Add(this.label7);
            this.groupBox5.Controls.Add(this.label6);
            this.groupBox5.Location = new System.Drawing.Point(400, 181);
            this.groupBox5.Name = "groupBox5";
            this.groupBox5.Size = new System.Drawing.Size(161, 194);
            this.groupBox5.TabIndex = 21;
            this.groupBox5.TabStop = false;
            this.groupBox5.Text = "Selected Mtw properties:";
            // 
            // yawLabel
            // 
            this.yawLabel.AutoSize = true;
            this.yawLabel.Location = new System.Drawing.Point(92, 160);
            this.yawLabel.Name = "yawLabel";
            this.yawLabel.Size = new System.Drawing.Size(10, 13);
            this.yawLabel.TabIndex = 11;
            this.yawLabel.Text = "-";
            this.yawLabel.TextAlign = System.Drawing.ContentAlignment.MiddleRight;
            // 
            // pitchLabel
            // 
            this.pitchLabel.AutoSize = true;
            this.pitchLabel.Location = new System.Drawing.Point(92, 132);
            this.pitchLabel.Name = "pitchLabel";
            this.pitchLabel.Size = new System.Drawing.Size(10, 13);
            this.pitchLabel.TabIndex = 10;
            this.pitchLabel.Text = "-";
            this.pitchLabel.TextAlign = System.Drawing.ContentAlignment.MiddleRight;
            // 
            // rollLabel
            // 
            this.rollLabel.AutoSize = true;
            this.rollLabel.Location = new System.Drawing.Point(92, 104);
            this.rollLabel.Name = "rollLabel";
            this.rollLabel.Size = new System.Drawing.Size(10, 13);
            this.rollLabel.TabIndex = 9;
            this.rollLabel.Text = "-";
            this.rollLabel.TextAlign = System.Drawing.ContentAlignment.MiddleRight;
            // 
            // effUpdateRateLabel
            // 
            this.effUpdateRateLabel.AutoSize = true;
            this.effUpdateRateLabel.Location = new System.Drawing.Point(92, 76);
            this.effUpdateRateLabel.Name = "effUpdateRateLabel";
            this.effUpdateRateLabel.Size = new System.Drawing.Size(10, 13);
            this.effUpdateRateLabel.TabIndex = 8;
            this.effUpdateRateLabel.Text = "-";
            this.effUpdateRateLabel.TextAlign = System.Drawing.ContentAlignment.MiddleRight;
            // 
            // rssiLabel
            // 
            this.rssiLabel.AutoSize = true;
            this.rssiLabel.Location = new System.Drawing.Point(92, 48);
            this.rssiLabel.Name = "rssiLabel";
            this.rssiLabel.Size = new System.Drawing.Size(10, 13);
            this.rssiLabel.TabIndex = 7;
            this.rssiLabel.Text = "-";
            this.rssiLabel.TextAlign = System.Drawing.ContentAlignment.MiddleRight;
            // 
            // batteryLevelLabel
            // 
            this.batteryLevelLabel.AutoSize = true;
            this.batteryLevelLabel.Location = new System.Drawing.Point(92, 20);
            this.batteryLevelLabel.Name = "batteryLevelLabel";
            this.batteryLevelLabel.Size = new System.Drawing.Size(10, 13);
            this.batteryLevelLabel.TabIndex = 6;
            this.batteryLevelLabel.Text = "-";
            this.batteryLevelLabel.TextAlign = System.Drawing.ContentAlignment.MiddleRight;
            // 
            // label11
            // 
            this.label11.AutoSize = true;
            this.label11.Location = new System.Drawing.Point(9, 160);
            this.label11.Name = "label11";
            this.label11.Size = new System.Drawing.Size(31, 13);
            this.label11.TabIndex = 5;
            this.label11.Text = "Yaw:";
            // 
            // label10
            // 
            this.label10.AutoSize = true;
            this.label10.Location = new System.Drawing.Point(9, 132);
            this.label10.Name = "label10";
            this.label10.Size = new System.Drawing.Size(34, 13);
            this.label10.TabIndex = 4;
            this.label10.Text = "Pitch:";
            // 
            // label9
            // 
            this.label9.AutoSize = true;
            this.label9.Location = new System.Drawing.Point(9, 104);
            this.label9.Name = "label9";
            this.label9.Size = new System.Drawing.Size(28, 13);
            this.label9.TabIndex = 3;
            this.label9.Text = "Roll:";
            // 
            // label8
            // 
            this.label8.AutoSize = true;
            this.label8.Location = new System.Drawing.Point(9, 76);
            this.label8.Name = "label8";
            this.label8.Size = new System.Drawing.Size(83, 13);
            this.label8.TabIndex = 2;
            this.label8.Text = "Eff. update rate:";
            // 
            // label7
            // 
            this.label7.AutoSize = true;
            this.label7.Location = new System.Drawing.Point(9, 48);
            this.label7.Name = "label7";
            this.label7.Size = new System.Drawing.Size(35, 13);
            this.label7.TabIndex = 1;
            this.label7.Text = "RSSI:";
            // 
            // label6
            // 
            this.label6.AutoSize = true;
            this.label6.Location = new System.Drawing.Point(9, 20);
            this.label6.Name = "label6";
            this.label6.Size = new System.Drawing.Size(68, 13);
            this.label6.TabIndex = 0;
            this.label6.Text = "Battery level:";
            // 
            // groupBox6
            // 
            this.groupBox6.Controls.Add(this.pictureBoxStateDiagram);
            this.groupBox6.Location = new System.Drawing.Point(567, 181);
            this.groupBox6.Name = "groupBox6";
            this.groupBox6.Size = new System.Drawing.Size(331, 180);
            this.groupBox6.TabIndex = 22;
            this.groupBox6.TabStop = false;
            this.groupBox6.Text = "State diagram:";
            // 
            // pictureBoxStateDiagram
            // 
            this.pictureBoxStateDiagram.Location = new System.Drawing.Point(7, 20);
            this.pictureBoxStateDiagram.Name = "pictureBoxStateDiagram";
            this.pictureBoxStateDiagram.Size = new System.Drawing.Size(318, 153);
            this.pictureBoxStateDiagram.TabIndex = 0;
            this.pictureBoxStateDiagram.TabStop = false;
            // 
            // pictureBox1
            // 
            this.pictureBox1.Image = ((System.Drawing.Image)(resources.GetObject("pictureBox1.Image")));
            this.pictureBox1.Location = new System.Drawing.Point(690, 13);
            this.pictureBox1.Name = "pictureBox1";
            this.pictureBox1.Size = new System.Drawing.Size(208, 162);
            this.pictureBox1.SizeMode = System.Windows.Forms.PictureBoxSizeMode.CenterImage;
            this.pictureBox1.TabIndex = 23;
            this.pictureBox1.TabStop = false;
            // 
            // AwindaMonitorDialog
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(910, 398);
            this.Controls.Add(this.pictureBox1);
            this.Controls.Add(this.groupBox6);
            this.Controls.Add(this.groupBox5);
            this.Controls.Add(this.groupBox4);
            this.Controls.Add(this.connectedMtwListGroupBox);
            this.Controls.Add(this.dockedMtwListGroupBox);
            this.Controls.Add(this.groupBox1);
            this.Controls.Add(this.labelDeviceId);
            this.Name = "AwindaMonitorDialog";
            this.Text = "Awinda Monitor Example";
            this.FormClosed += new System.Windows.Forms.FormClosedEventHandler(this.AwindaMonitorDialog_FormClosed);
            this.groupBox1.ResumeLayout(false);
            this.groupBox1.PerformLayout();
            this.dockedMtwListGroupBox.ResumeLayout(false);
            this.connectedMtwListGroupBox.ResumeLayout(false);
            this.connectedMtwListGroupBox.PerformLayout();
            this.groupBox4.ResumeLayout(false);
            this.groupBox5.ResumeLayout(false);
            this.groupBox5.PerformLayout();
            this.groupBox6.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.pictureBoxStateDiagram)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.pictureBox1)).EndInit();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Button btnEnable;
        private System.Windows.Forms.Button btnMeasure;
        private System.Windows.Forms.Button btnRecord;
        private System.Windows.Forms.Label labelDevId;
        private System.Windows.Forms.Label labelDeviceId;
        private System.Windows.Forms.ComboBox comboBoxChannel;
        private System.Windows.Forms.Label labelChannel;
        private System.Windows.Forms.GroupBox groupBox1;
        private System.Windows.Forms.Label labelUpdateRate;
        private System.Windows.Forms.ProgressBar progressBarFlushing;
        private System.Windows.Forms.Label labelFlushing;
        private System.Windows.Forms.TextBox textBoxFilename;
        private System.Windows.Forms.Label labelFilename;
        private System.Windows.Forms.ComboBox comboBoxUpdateRate;
        private System.Windows.Forms.GroupBox dockedMtwListGroupBox;
        private System.Windows.Forms.GroupBox connectedMtwListGroupBox;
        private System.Windows.Forms.CheckBox checkBoxPitchToSelect;
        private System.Windows.Forms.GroupBox groupBox4;
        private System.Windows.Forms.GroupBox groupBox5;
        private System.Windows.Forms.RichTextBox logWindow;
        private System.Windows.Forms.Label label11;
        private System.Windows.Forms.Label label10;
        private System.Windows.Forms.Label label9;
        private System.Windows.Forms.Label label8;
        private System.Windows.Forms.Label label7;
        private System.Windows.Forms.Label label6;
        private System.Windows.Forms.Label yawLabel;
        private System.Windows.Forms.Label pitchLabel;
        private System.Windows.Forms.Label rollLabel;
        private System.Windows.Forms.Label effUpdateRateLabel;
        private System.Windows.Forms.Label rssiLabel;
        private System.Windows.Forms.Label batteryLevelLabel;
        private System.Windows.Forms.GroupBox groupBox6;
        private System.Windows.Forms.PictureBox pictureBox1;
        private System.Windows.Forms.Label labelStationId;
        private System.Windows.Forms.PictureBox pictureBoxStateDiagram;
        private System.Windows.Forms.ListBox dockedMtwList;
        private System.Windows.Forms.ListBox connectedMtwList;
    }
}

