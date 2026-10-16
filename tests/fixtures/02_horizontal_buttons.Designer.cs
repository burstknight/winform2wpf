namespace HorizontalButtons
{
    partial class Form2
    {
        private System.ComponentModel.IContainer components = null;
        private System.Windows.Forms.Button button1;
        private System.Windows.Forms.Button button2;
        private System.Windows.Forms.Button button3;

        private void InitializeComponent()
        {
            this.button1 = new System.Windows.Forms.Button();
            this.button2 = new System.Windows.Forms.Button();
            this.button3 = new System.Windows.Forms.Button();
            this.SuspendLayout();
            // 
            // button1
            // 
            this.button1.Name = "button1";
            this.button1.Text = "OK";
            this.button1.Location = new System.Drawing.Point(12, 12);
            this.button1.Size = new System.Drawing.Size(75, 23);
            // 
            // button2
            // 
            this.button2.Name = "button2";
            this.button2.Text = "Cancel";
            this.button2.Location = new System.Drawing.Point(93, 12);
            this.button2.Size = new System.Drawing.Size(75, 23);
            // 
            // button3
            // 
            this.button3.Name = "button3";
            this.button3.Text = "Apply";
            this.button3.Location = new System.Drawing.Point(174, 12);
            this.button3.Size = new System.Drawing.Size(75, 23);
            // 
            // Form2
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(261, 47);
            this.Controls.Add(this.button1);
            this.Controls.Add(this.button2);
            this.Controls.Add(this.button3);
            this.Name = "Form2";
            this.Text = "Buttons";
            this.ResumeLayout(false);
        }
    }
}
