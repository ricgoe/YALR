<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'

const emit = defineEmits<{
  (event: 'uploaded', payload: unknown): void
  (event: 'upload-error', error: string): void
}>()

const previewRef = ref<HTMLVideoElement | null>(null)
const playbackRef = ref<HTMLVideoElement | null>(null)
const mediaStream = ref<MediaStream | null>(null)
const mediaRecorder = ref<MediaRecorder | null>(null)
const recordedChunks = ref<Blob[]>([])
const videoBlob = ref<Blob>()
const recordedUrl = ref<string | null>(null)
const isRecording = ref(false)
const isInitializing = ref(false)
const errorMessage = ref<string | null>(null)
const isUploading = ref(false)
const hypo = ref("")
const isSupported =
  typeof window !== 'undefined' &&
  'MediaRecorder' in window &&
  typeof navigator !== 'undefined' &&
  'mediaDevices' in navigator
const canStartRecording = computed(
  () => isSupported && !isInitializing.value && !isRecording.value
)
async function initStream() {
  if (!isSupported || mediaStream.value || isInitializing.value) return
  isInitializing.value = true
  errorMessage.value = null
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: true
    })
    mediaStream.value = stream
  } catch (error) {
    if (error instanceof Error) {
      errorMessage.value = error.message
    } else {
      errorMessage.value = 'Unable to access camera or microphone'
    }
  } finally {
    isInitializing.value = false
  }
}
async function startRecording() {
  errorMessage.value = null
  if (!isSupported) {
    errorMessage.value = 'MediaRecorder API is not supported in this browser.'
    return
  }
  if (!mediaStream.value) {
    await initStream()
  }
  if (!mediaStream.value) return
  if (recordedUrl.value) {
    URL.revokeObjectURL(recordedUrl.value)
    recordedUrl.value = null
  }
  recordedChunks.value = []
  try {
    const recorder = new MediaRecorder(mediaStream.value)
    recorder.addEventListener('dataavailable', handleDataAvailable)
    recorder.addEventListener('stop', handleStop)
    recorder.start()
    mediaRecorder.value = recorder
    isRecording.value = true
  } catch (error) {
    if (error instanceof Error) {
      errorMessage.value = error.message
    } else {
      errorMessage.value = 'Recording failed to start.'
    }
  }
}
function stopRecording() {
  if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') {
    mediaRecorder.value.stop()
  }
  isRecording.value = false
}
function resetRecording() {
  if (recordedUrl.value) {
    URL.revokeObjectURL(recordedUrl.value)
    recordedUrl.value = null
  }
  recordedChunks.value = []
}
function handleDataAvailable(event: BlobEvent) {
  if (event.data && event.data.size > 0) {
    recordedChunks.value.push(event.data)
  }
}
async function handleStop() {
  const mimeType =
    mediaRecorder.value?.mimeType || 'video/webm;codecs=vp8,opus'
  if (recordedChunks.value.length === 0) return
  const blob = new Blob(recordedChunks.value, { type: mimeType })
  recordedUrl.value = URL.createObjectURL(blob)
  isRecording.value = false
  if (playbackRef.value) {
    playbackRef.value.src = recordedUrl.value
  }
  videoBlob.value = blob 
}
function stopStream() {
  mediaStream.value?.getTracks().forEach((track) => track.stop())
  mediaStream.value = null
}
const base = import.meta.env.DEV ? "http://10.40.25.19:8000" : "";

async function uploadRecording() {
  const response = await fetch(`${base}/upload-video`, {
    method: "POST",
    headers: {
      "Content-Type": videoBlob.value?.type || "video/webm",
    },
    body: videoBlob.value,
  });

  if (!response.ok) {
    throw new Error(`Upload failed: ${response.statusText}`);
  }

  const result = await response.json();
  hypo.value = result.message;
}

watch(mediaStream, (stream) => {
  const video = previewRef.value
  if (!video) return
  video.srcObject = stream
  if (stream) {
    void video.play().catch(() => undefined)
  } else {
    video.pause()
  }
})
onMounted(() => {
  if (isSupported) {
    void initStream()
  } else {
    errorMessage.value = 'MediaRecorder API is not supported in this browser.'
  }
})
onBeforeUnmount(() => {
  if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') {
    mediaRecorder.value.stop()
  }
  stopStream()
  if (recordedUrl.value) {
    URL.revokeObjectURL(recordedUrl.value)
  }
})
</script>
<template>
  <div class="video-recorder">
    <div class="preview">
      <video ref="previewRef" autoplay playsinline muted></video>
      <div v-if="!isSupported" class="message">
        Your browser does not support camera recording.
      </div>
    </div>
    <div class="controls">
      <button type="button" @click="startRecording" :disabled="!canStartRecording">
        {{ isInitializing ? 'Initializing…' : 'Start Recording' }}
      </button>
      <button type="button" @click="stopRecording" :disabled="!isRecording">
        Stop Recording
      </button>
      <button
        type="button"
        @click="resetRecording"
        :disabled="!recordedUrl || isRecording"
      >
        Reset
      </button>
      <button type="button" @click="uploadRecording" >upload</button>
    </div>
    <p v-if="errorMessage" class="message error">{{ errorMessage }}</p>
    <p v-if="isUploading" class="message">Uploading…</p>
    <div v-if="recordedUrl" class="playback">
      <video ref="playbackRef" controls :src="recordedUrl"></video>
      <a
        class="download"
        :href="recordedUrl"
        download="recording.webm"
      >
        Download recording
      </a>
    </div>
    <span>{{ hypo }}</span>
  </div>
</template>
<style scoped>
.video-recorder {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-width: 480px;
}
.preview video,
.playback video {
  width: 100%;
  border-radius: 0.5rem;
  background: #000;
}
.controls {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}
.controls button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.375rem;
  background: #1f7aec;
  color: #fff;
  cursor: pointer;
  transition: background 0.2s ease;
}
.controls button:disabled {
  background: #9bbcee;
  cursor: not-allowed;
}
.controls button:not(:disabled):hover {
  background: #155bbf;
}
.message {
  margin-top: 0.5rem;
  color: #666;
}
.message.error {
  color: #d1434b;
}
.download {
  display: inline-block;
  margin-top: 0.5rem;
  color: #1f7aec;
}
</style>
