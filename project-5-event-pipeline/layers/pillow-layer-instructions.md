# Adding the Pillow Layer to Your Lambda Function

The image processing Lambda function requires the **Pillow** library for image manipulation. Since Pillow is not included in the AWS Lambda Python runtime, you need to add it as a Lambda Layer.

## Option 1: Use a Pre-Built ARN (Easiest)

The Klayers project maintains pre-built Lambda layers for popular Python packages.

1. Go to: https://github.com/keithrozario/Klayers
2. Find the ARN for Pillow for your region and Python version
3. In your Lambda function → **Layers** → **Add a layer** → **Specify an ARN**
4. Paste the ARN (e.g., `arn:aws:lambda:us-east-1:770693421928:layer:Klayers-p312-Pillow:2`)

## Option 2: Build Your Own Layer

If you want to build it yourself:

### On a Linux/Mac machine (or AWS CloudShell):

```bash
mkdir -p python
pip install Pillow -t python/
zip -r pillow-layer.zip python/
```

### Upload as a Lambda Layer:

1. Go to **Lambda → Layers → Create layer**
2. **Name**: `pillow-layer`
3. **Upload** the `pillow-layer.zip` file
4. **Compatible runtimes**: Python 3.12
5. Click **Create**
6. Go to your Lambda function → **Layers** → **Add a layer** → **Custom layers** → Select `pillow-layer`

## Option 3: Use AWS CloudShell (No Local Setup Needed)

1. Open **AWS CloudShell** (top-right corner of AWS Console)
2. Run:
```bash
mkdir -p python
pip install Pillow -t python/
zip -r pillow-layer.zip python/
aws lambda publish-layer-version \
    --layer-name pillow-layer \
    --zip-file fileb://pillow-layer.zip \
    --compatible-runtimes python3.12
```
3. Note the Layer ARN from the output
4. Add it to your Lambda function
