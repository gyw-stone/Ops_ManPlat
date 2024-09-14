{{/* Select labels */}}
{{- define "zk.selectorLabels" -}}
app: zk
{{- end }}

{{/* zookeeper env */}}
{{- define "zk.env" -}}
- name: SERVERS
  value: {{ .Values.replicaCount | quote }}
- name: ZOO_CONF_DIR
  value: /conf
- name: ZOO_DATA_DIR
  value: /data
- name: ZOO_LOG_DIR
  value: /datalog
{{- end }}
