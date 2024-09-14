{{/* Kafka labels */}}
{{- define "kafka.selectorLabels" -}}
app: kafka
{{- end }}
{{/* Kafka Env */}}
{{- define "kafka.env" -}}
- name: SERVERS
  value: {{ .Values.replicaCount | quote }}
- name: KAFKA_LISTENERS
  value: "PLAINTEXT://:9092"
- name: KAFKA_ZOOKEEPER_CONNECT
  value: "{{ .Release.Name }}-{{ .Values.global.chartName }}-client-service.ns-{{ .Release.Name }}.svc.cluster.local:2181"
- name: KAFKA_PORT
  value: "9092"
- name: KAFKA_MESSAGE_MAX_BYTES
  value: "2000000"
{{- end }}
