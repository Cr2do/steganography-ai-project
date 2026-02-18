import { Component, OnDestroy, signal } from '@angular/core';

type VerificationMode = 'none' | 'ai' | 'signature';

@Component({
  selector: 'app-verfication',
  imports: [],
  templateUrl: './verfication.html',
  styleUrl: './verfication.css',
})
export class Verfication {
  readonly mode = signal<VerificationMode>('none');
  readonly selectedFile = signal<File | null>(null);
  readonly previewUrl = signal<string | null>(null);
  readonly resultMessage = signal<string | null>(null);

  setMode(mode: VerificationMode) {
    this.mode.set(mode);
    this.resultMessage.set(null);
  }

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0] ?? null;

    this.selectedFile.set(file);
    this.resultMessage.set(null);

    const currentPreviewUrl = this.previewUrl();
    if (currentPreviewUrl) {
      URL.revokeObjectURL(currentPreviewUrl);
    }
    this.previewUrl.set(file ? URL.createObjectURL(file) : null);
  }

  runAiCheck() {
    if (!this.selectedFile()) {
      this.resultMessage.set('Please select an image first.');
      return;
    }

    this.resultMessage.set('AI analysis placeholder: ready to send the image to the backend.');
  }

  runSignatureCheck() {
    if (!this.selectedFile()) {
      this.resultMessage.set('Please select an image first.');
      return;
    }

    this.resultMessage.set('Signature verification placeholder: ready to verify the image signature.');
  }

  ngOnDestroy(): void {
    const currentPreviewUrl = this.previewUrl();
    if (currentPreviewUrl) {
      URL.revokeObjectURL(currentPreviewUrl);
    }
  }
}
