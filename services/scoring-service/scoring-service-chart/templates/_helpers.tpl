{{/*
Expand the name of the chart.
*/}}
{{- define "scoring-service-chart.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "scoring-service-chart.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "scoring-service-chart.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "scoring-service-chart.labels" -}}
helm.sh/chart: {{ include "scoring-service-chart.chart" . }}
{{ include "scoring-service-chart.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "scoring-service-chart.selectorLabels" -}}
app.kubernetes.io/name: {{ include "scoring-service-chart.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "scoring-service-chart.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "scoring-service-chart.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}


{{/* Имя Deployment */}}
{{- define "scoring-service.fullname.release" -}}
{{ .Release.Name }}
{{- end }}

{{/* Лейблы для ресурсов */}}
{{- define "scoring-service.selectorLabels.custom" -}}
app: scoring-service
student: {{ .Values.student.name | quote }}
{{- end }}

{{/* Имя configmap */}}
{{- define "scoring-service.configmap.name" -}}
scoring-service-config-{{ .Values.student.name | lower }}
{{- end }}

{{/* Имя контейнера */}}
{{- define "scoring-service-container.name" -}}
scoring-service-container
{{- end }}
