namespace NestedPanel
{
    partial class Form6
    {
        private System.ComponentModel.IContainer components = null;
        private System.Windows.Forms.Panel outerPanel;
        private System.Windows.Forms.Panel innerPanel;
        private System.Windows.Forms.Button button1;

        private void InitializeComponent()
        {
            this.outerPanel = new System.Windows.Forms.Panel();
            this.innerPanel = new System.Windows.Forms.Panel();
            this.button1 = new System.Windows.Forms.Button();
            this.outerPanel.SuspendLayout();
            this.innerPanel.SuspendLayout();
            this.SuspendLayout();
            // 
            // outerPanel
            // 
            this.outerPanel.Name = "outerPanel";
            this.outerPanel.Location = new System.Drawing.Point(12, 12);
            this.outerPanel.Size = new System.Drawing.Size(260, 150);
            this.outerPanel.Controls.Add(this.innerPanel);
            // 
            // innerPanel
            // 
            this.innerPanel.Name = "innerPanel";
            this.innerPanel.Location = new System.Drawing.Point(10, 10);
            this.innerPanel.Size = new System.Drawing.Size(200, 60);
            this.innerPanel.Controls.Add(this.button1);
            // 
            // button1
            // 
            this.button1.Name = "button1";
            this.button1.Text = "Nested";
            this.button1.Location = new System.Drawing.Point(10, 10);
            this.button1.Size = new System.Drawing.Size(75, 23);
            // 
            // Form6
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(284, 174);
            this.Controls.Add(this.outerPanel);
            this.Name = "Form6";
            this.Text = "Nested";
            this.outerPanel.ResumeLayout(false);
            this.innerPanel.ResumeLayout(false);
            this.ResumeLayout(false);
        }
    }
}
