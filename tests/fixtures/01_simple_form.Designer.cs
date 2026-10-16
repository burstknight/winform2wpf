namespace SimpleForm
{
    partial class Form1
    {
        private System.ComponentModel.IContainer components = null;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.TextBox textBox1;
        private System.Windows.Forms.Button button1;

        private void InitializeComponent()
        {
            this.label1 = new System.Windows.Forms.Label();
            this.textBox1 = new System.Windows.Forms.TextBox();
            this.button1 = new System.Windows.Forms.Button();
            this.SuspendLayout();
            // 
            // label1
            // 
            this.label1.Name = "label1";
            this.label1.Text = "Username";
            this.label1.Location = new System.Drawing.Point(12, 15);
            this.label1.Size = new System.Drawing.Size(80, 20);
            // 
            // textBox1
            // 
            this.textBox1.Name = "textBox1";
            this.textBox1.Location = new System.Drawing.Point(98, 12);
            this.textBox1.Size = new System.Drawing.Size(160, 20);
            // 
            // button1
            // 
            this.button1.Name = "button1";
            this.button1.Text = "Login";
            this.button1.Location = new System.Drawing.Point(98, 48);
            this.button1.Size = new System.Drawing.Size(75, 23);
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(284, 92);
            this.Controls.Add(this.label1);
            this.Controls.Add(this.textBox1);
            this.Controls.Add(this.button1);
            this.Name = "Form1";
            this.Text = "Login";
            this.ResumeLayout(false);
            this.PerformLayout();
        }
    }
}
