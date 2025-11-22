
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

﻿namespace MTwExample
{
    partial class Form1
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
			this.components = new System.ComponentModel.Container();
			this.btnScan = new System.Windows.Forms.Button();
			this.btnEnable = new System.Windows.Forms.Button();
			this.lblChannel = new System.Windows.Forms.Label();
			this.cbxStations = new System.Windows.Forms.ComboBox();
			this.lblDeviceCount = new System.Windows.Forms.Label();
			this.btnMeasure = new System.Windows.Forms.Button();
			this.btnStop = new System.Windows.Forms.Button();
			this.timer1 = new System.Windows.Forms.Timer(this.components);
			this.rtbSteps = new System.Windows.Forms.RichTextBox();
			this.rtbData = new System.Windows.Forms.RichTextBox();
			this.cbxChannel = new System.Windows.Forms.ComboBox();
			this.btnRecord = new System.Windows.Forms.Button();
			this.textBoxFilename = new System.Windows.Forms.TextBox();
			this.SuspendLayout();
			// 
			// btnScan
			// 
			this.btnScan.Location = new System.Drawing.Point(13, 12);
			this.btnScan.Name = "btnScan";
			this.btnScan.Size = new System.Drawing.Size(92, 23);
			this.btnScan.TabIndex = 0;
			this.btnScan.Text = "Scan";
			this.btnScan.UseVisualStyleBackColor = true;
			this.btnScan.Click += new System.EventHandler(this.btnScan_Click);
			// 
			// btnEnable
			// 
			this.btnEnable.Enabled = false;
			this.btnEnable.Location = new System.Drawing.Point(12, 121);
			this.btnEnable.Name = "btnEnable";
			this.btnEnable.Size = new System.Drawing.Size(92, 23);
			this.btnEnable.TabIndex = 3;
			this.btnEnable.Text = "Enable Radio";
			this.btnEnable.UseVisualStyleBackColor = true;
			this.btnEnable.Click += new System.EventHandler(this.btnEnable_Click);
			// 
			// lblChannel
			// 
			this.lblChannel.AutoSize = true;
			this.lblChannel.Location = new System.Drawing.Point(16, 82);
			this.lblChannel.Name = "lblChannel";
			this.lblChannel.Size = new System.Drawing.Size(49, 13);
			this.lblChannel.TabIndex = 4;
			this.lblChannel.Text = "Channel:";
			// 
			// cbxStations
			// 
			this.cbxStations.FormattingEnabled = true;
			this.cbxStations.Location = new System.Drawing.Point(13, 51);
			this.cbxStations.Name = "cbxStations";
			this.cbxStations.Size = new System.Drawing.Size(290, 21);
			this.cbxStations.TabIndex = 5;
			// 
			// lblDeviceCount
			// 
			this.lblDeviceCount.AutoSize = true;
			this.lblDeviceCount.Location = new System.Drawing.Point(120, 164);
			this.lblDeviceCount.Name = "lblDeviceCount";
			this.lblDeviceCount.Size = new System.Drawing.Size(105, 13);
			this.lblDeviceCount.TabIndex = 6;
			this.lblDeviceCount.Text = "MTw\'s Connected: 0";
			// 
			// btnMeasure
			// 
			this.btnMeasure.Enabled = false;
			this.btnMeasure.Location = new System.Drawing.Point(12, 159);
			this.btnMeasure.Name = "btnMeasure";
			this.btnMeasure.Size = new System.Drawing.Size(92, 23);
			this.btnMeasure.TabIndex = 8;
			this.btnMeasure.Text = "Measure";
			this.btnMeasure.UseVisualStyleBackColor = true;
			this.btnMeasure.Click += new System.EventHandler(this.btnMeasure_Click);
			// 
			// btnStop
			// 
			this.btnStop.Enabled = false;
			this.btnStop.Location = new System.Drawing.Point(13, 235);
			this.btnStop.Name = "btnStop";
			this.btnStop.Size = new System.Drawing.Size(91, 23);
			this.btnStop.TabIndex = 9;
			this.btnStop.Text = "Stop";
			this.btnStop.UseVisualStyleBackColor = true;
			this.btnStop.Click += new System.EventHandler(this.btnStop_Click);
			// 
			// timer1
			// 
			this.timer1.Tick += new System.EventHandler(this.timer1_Tick);
			// 
			// rtbSteps
			// 
			this.rtbSteps.Location = new System.Drawing.Point(333, 12);
			this.rtbSteps.Name = "rtbSteps";
			this.rtbSteps.ReadOnly = true;
			this.rtbSteps.Size = new System.Drawing.Size(326, 233);
			this.rtbSteps.TabIndex = 10;
			this.rtbSteps.Text = "";
			// 
			// rtbData
			// 
			this.rtbData.Font = new System.Drawing.Font("Courier New", 9.75F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
			this.rtbData.Location = new System.Drawing.Point(12, 273);
			this.rtbData.Name = "rtbData";
			this.rtbData.Size = new System.Drawing.Size(647, 204);
			this.rtbData.TabIndex = 11;
			this.rtbData.Text = "";
			// 
			// cbxChannel
			// 
			this.cbxChannel.DisplayMember = "19";
			this.cbxChannel.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
			this.cbxChannel.FormattingEnabled = true;
			this.cbxChannel.Items.AddRange(new object[] {
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
			this.cbxChannel.Location = new System.Drawing.Point(71, 77);
			this.cbxChannel.Name = "cbxChannel";
			this.cbxChannel.Size = new System.Drawing.Size(73, 21);
			this.cbxChannel.TabIndex = 12;
			// 
			// btnRecord
			// 
			this.btnRecord.Enabled = false;
			this.btnRecord.Location = new System.Drawing.Point(12, 197);
			this.btnRecord.Name = "btnRecord";
			this.btnRecord.Size = new System.Drawing.Size(92, 23);
			this.btnRecord.TabIndex = 13;
			this.btnRecord.Text = "Record";
			this.btnRecord.UseVisualStyleBackColor = true;
			this.btnRecord.Click += new System.EventHandler(this.btnRecord_Click);
			// 
			// textBoxFilename
			// 
			this.textBoxFilename.Location = new System.Drawing.Point(123, 200);
			this.textBoxFilename.Name = "textBoxFilename";
			this.textBoxFilename.Size = new System.Drawing.Size(86, 20);
			this.textBoxFilename.TabIndex = 21;
			this.textBoxFilename.Text = "logfile.mtb";
			// 
			// Form1
			// 
			this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
			this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
			this.ClientSize = new System.Drawing.Size(671, 489);
			this.Controls.Add(this.textBoxFilename);
			this.Controls.Add(this.btnRecord);
			this.Controls.Add(this.cbxChannel);
			this.Controls.Add(this.rtbData);
			this.Controls.Add(this.rtbSteps);
			this.Controls.Add(this.btnStop);
			this.Controls.Add(this.btnMeasure);
			this.Controls.Add(this.lblDeviceCount);
			this.Controls.Add(this.cbxStations);
			this.Controls.Add(this.lblChannel);
			this.Controls.Add(this.btnEnable);
			this.Controls.Add(this.btnScan);
			this.Name = "Form1";
			this.Text = "MTw Example";
			this.FormClosed += new System.Windows.Forms.FormClosedEventHandler(this.Form1_FormClosed);
			this.ResumeLayout(false);
			this.PerformLayout();

        }

        #endregion

		private System.Windows.Forms.Button btnScan;
        private System.Windows.Forms.Button btnEnable;
        private System.Windows.Forms.Label lblChannel;
        private System.Windows.Forms.ComboBox cbxStations;
		private System.Windows.Forms.Label lblDeviceCount;
        private System.Windows.Forms.Button btnMeasure;
        private System.Windows.Forms.Button btnStop;
        private System.Windows.Forms.Timer timer1;
        private System.Windows.Forms.RichTextBox rtbSteps;
        private System.Windows.Forms.RichTextBox rtbData;
		private System.Windows.Forms.ComboBox cbxChannel;
		private System.Windows.Forms.Button btnRecord;
		private System.Windows.Forms.TextBox textBoxFilename;
    }
}

