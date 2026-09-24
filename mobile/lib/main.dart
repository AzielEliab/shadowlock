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
      theme: buildAppTheme(Brightness.light),
      darkTheme: buildAppTheme(Brightness.dark),
      themeMode: ThemeMode.system,
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
        'Compared the text on this screen. Nothing was saved.',
        'Observed words: $ow',
        'Guess words: $cw',
        'Word-count gap: $delta',
        'Observed id: ${_hid(obs)}',
        'Guess id: ${_hid(cf)}',
        'Ids are sha256 hex, first 12 characters.',
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
      appBar: AppBar(
        title: const Text('ShadowLock'),
        actions: const [
          Padding(
            padding: EdgeInsets.only(right: 16),
            child: Center(child: Text('Aziel Eliab')),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text(
            'Compare a finished job',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 8),
          const Text(
            'Type the job you already finished. ShadowLock counts the words, '
            'hashes the text, and keeps the result on this screen only.',
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _observed,
            maxLines: 6,
            decoration: const InputDecoration(
              labelText: 'Finished job',
              alignLabelWithHint: true,
            ),
          ),
          const SizedBox(height: 16),
          FilledButton(onPressed: _makeReport, child: const Text('Show report')),
          const SizedBox(height: 8),
          OutlinedButton(onPressed: _forget, child: const Text('Forget')),
          const SizedBox(height: 16),
          ExpansionTile(
            title: const Text('Advanced'),
            children: [
              TextField(
                controller: _counterfactual,
                maxLines: 6,
                decoration: const InputDecoration(
                  labelText: 'Guess',
                  alignLabelWithHint: true,
                ),
              ),
              const SizedBox(height: 8),
            ],
          ),
          ExpansionTile(
            title: const Text('About'),
            children: const [
              Padding(
                padding: EdgeInsets.only(bottom: 12),
                child: Text(
                  'Author: Aziel Eliab. This screen reports word counts and '
                  'hashed ids for the text you type. It does not write a file. '
                  'The desktop command shadowlock ui compares money on a job file.',
                ),
              ),
            ],
          ),
          if (_report != null) ...[
            const SizedBox(height: 8),
            Text('Simple summary', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
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
