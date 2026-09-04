import 'dart:convert';

import 'package:crypto/crypto.dart';
import 'package:flutter/material.dart';

import 'theme.dart';

void main() {
  runApp(const ShadowLockApp());
}

class ShadowLockApp extends StatelessWidget {
  const ShadowLockApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'ShadowLock',
      debugShowCheckedModeBanner: false,
      theme: buildAppTheme(),
      home: const MirrorPage(),
    );
  }
}

class MirrorPage extends StatefulWidget {
  const MirrorPage({super.key});

  @override
  State<MirrorPage> createState() => _MirrorPageState();
}

class _MirrorPageState extends State<MirrorPage> {
  final _observed = TextEditingController();
  final _counterfactual = TextEditingController();
  String? _report;

  @override
  void dispose() {
    _observed.dispose();
    _counterfactual.dispose();
    super.dispose();
  }

  String _hid(String s) {
    final h = sha256.convert(utf8.encode(s)).toString();
    return h.substring(0, 12);
  }

  void _makeReport() {
    final obs = _observed.text;
    final cf = _counterfactual.text;
    final ow = obs.trim().isEmpty ? 0 : obs.trim().split(RegExp(r'\s+')).length;
    final cw = cf.trim().isEmpty ? 0 : cf.trim().split(RegExp(r'\s+')).length;
    final delta = ow - cw;
    setState(() {
      _report = [
        'ShadowLock report (anonymous aggregate; session only)',
        'observed_hashed_id: ${_hid(obs)}',
        'counterfactual_hashed_id: ${_hid(cf)}',
        'observed_chars: ${obs.length}',
        'counterfactual_chars: ${cf.length}',
        'observed_words: $ow',
        'counterfactual_words: $cw',
        'word_count_variance: $delta',
        'sample_rate_target: 0.2  (1-in-5 on streamed jobs; this screen reports the pair you typed)',
        'notes:',
        '- Identifiers are sha256 hex[:12] only.',
        '- No person, team, or department names are emitted.',
        '- Zero-retention: this report lives in RAM until Forget.',
        '- Change is optional. Truth is not.',
      ].join('\n');
    });
  }

  void _forget() {
    setState(() {
      _observed.clear();
      _counterfactual.clear();
      _report = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('ShadowLock')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text(
            'Change is optional. Truth is not.',
            style: TextStyle(color: kGold, fontStyle: FontStyle.italic, fontSize: 16),
          ),
          const SizedBox(height: 8),
          const Text(
            'Zero-retention outcome mirror. OS-hooks into AZ-OS under ethics '
            'policy. Nothing is stored. Not a dispatcher, optimizer, scheduler, '
            'or learning system.',
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _observed,
            maxLines: 6,
            decoration: const InputDecoration(
              labelText: 'Observed outcome',
              alignLabelWithHint: true,
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _counterfactual,
            maxLines: 6,
            decoration: const InputDecoration(
              labelText: 'Counterfactual expectation',
              alignLabelWithHint: true,
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              FilledButton(onPressed: _makeReport, child: const Text('Report')),
              const SizedBox(width: 8),
              OutlinedButton(onPressed: _forget, child: const Text('Forget')),
            ],
          ),
          const SizedBox(height: 8),
          const Text(
            'Forget drops both fields and the report. No .shadowlock store, no sqlite, no job log.',
            style: TextStyle(color: kGoldDim, fontSize: 12),
          ),
          if (_report != null) ...[
            const SizedBox(height: 16),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: SelectableText(
                  _report!,
                  style: const TextStyle(fontFamily: 'monospace', fontSize: 13, height: 1.4),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
