import 'dart:async';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'api_service.dart';

void main() {
  runApp(const GrammarGuardApp());
  BackendManager.startBackend();
}

class BackendManager {
  static Process? _process;

  static Future<void> startBackend() async {
    String pythonExecutable = 'python';
    String scriptPath = 'backend/main.py';

    if (Platform.isWindows) {
      print("Current Working Directory: ${Directory.current.path}");

      final candidates = [
        // If running from project root
        {
          'python': r'.\venv\Scripts\python.exe',
          'script': r'.\backend\main.py',
        },
        // If running from frontend/ (Development)
        {
          'python': r'..\venv\Scripts\python.exe',
          'script': r'..\backend\main.py',
        },
        // If running from build/windows/runner/Debug
        {
          'python': r'..\..\..\..\venv\Scripts\python.exe',
          'script': r'..\..\..\..\backend\main.py',
        },
        // Fallback relative to typical release location
        {
          'python': r'data\flutter_assets\..\venv\Scripts\python.exe',
          'script': r'data\flutter_assets\..\backend\main.py',
        },
      ];

      bool found = false;
      for (final paths in candidates) {
        var pyFile = File(paths['python']!);
        if (await pyFile.exists()) {
          pythonExecutable = paths['python']!;
          scriptPath = paths['script']!;
          print("Found Python environment at: ${pyFile.absolute.path}");
          found = true;
          break;
        }
      }

      if (!found) {
        print(
          "WARNING: Could not find venv python.exe in candidate paths. Trying default global python.",
        );
        // If we are in frontend, script needs to be ../backend/main.py roughly
        if (File(r'..\backend\main.py').existsSync()) {
          scriptPath = r'..\backend\main.py';
        }
      }
    } else {
      pythonExecutable =
          '../venv/bin/python'; // Simplify for non-windows for now
    }

    print("Attempting to start backend with: $pythonExecutable $scriptPath");

    try {
      _process = await Process.start(
        pythonExecutable,
        [scriptPath],
        runInShell: false,
        mode: ProcessStartMode
            .detached, // Detach so it survives simple app restarts if needed
      );
      print("Backend process started (PID: ${_process!.pid})");

      // Note: Stdout/Stderr might not work well in detached mode depending on OS,
      // but detached prevents 'zombie' locks sometimes.
      // Actually, for dev, normal mode is better to see errors.
    } catch (e) {
      print("CRITICAL ERROR starting backend: $e");
    }
  }

  static void stopBackend() {
    _process?.kill();
  }
}

class GrammarGuardApp extends StatelessWidget {
  const GrammarGuardApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'GrammarGuard',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF6C63FF),
          brightness: Brightness.dark,
          surface: const Color(0xFF1E1E2E), // Deep dark background
        ),
        textTheme: GoogleFonts.interTextTheme(ThemeData.dark().textTheme),
      ),
      home: const HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final TextEditingController _controller = TextEditingController();
  final ApiService _apiService = ApiService();
  String _status = "Initializing...";
  String _result = "";
  bool _isBackendReady = false;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _checkBackendStatus();
  }

  Future<void> _checkBackendStatus() async {
    // Poll the backend until it's ready
    int retries = 0;
    while (retries < 20) {
      bool ready = await _apiService.checkHealth();
      if (ready) {
        if (mounted) {
          setState(() {
            _isBackendReady = true;
            _status = "Ready";
          });
        }
        return;
      }
      await Future.delayed(const Duration(seconds: 1));
      retries++;
      if (mounted)
        setState(() => _status = "Loading NLP Model... ($retries/20)");
    }
    if (mounted) setState(() => _status = "Backend Connection Failed");
  }

  Future<void> _analyzeText() async {
    if (_controller.text.isEmpty) return;

    setState(() {
      _isLoading = true;
      _result = "";
    });

    try {
      final response = await _apiService.checkGrammar(_controller.text);
      // For now, just show the placeholder 'corrected_text'
      setState(() {
        _result = response['corrected_text'] ?? "No result";
      });
    } catch (e) {
      setState(() {
        _result = "Error: $e";
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF1E1E2E), // Consistent background
      body: Center(
        child: Container(
          constraints: const BoxConstraints(maxWidth: 800),
          padding: const EdgeInsets.all(32),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Row(
                children: [
                  const Icon(
                    Icons.security,
                    color: Color(0xFF6C63FF),
                    size: 32,
                  ),
                  const SizedBox(width: 12),
                  Text(
                    "GrammarGuard",
                    style: GoogleFonts.outfit(
                      fontSize: 28,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  const Spacer(),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 6,
                    ),
                    decoration: BoxDecoration(
                      color: _isBackendReady
                          ? Colors.green.withOpacity(0.2)
                          : Colors.orange.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(
                        color: _isBackendReady ? Colors.green : Colors.orange,
                        width: 1,
                      ),
                    ),
                    child: Text(
                      _status,
                      style: TextStyle(
                        color: _isBackendReady
                            ? Colors.greenAccent
                            : Colors.orangeAccent,
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 40),

              // Main Input Area
              Expanded(
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Input Column
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            "Input Text",
                            style: TextStyle(color: Colors.white70),
                          ),
                          const SizedBox(height: 8),
                          Expanded(
                            child: Container(
                              decoration: BoxDecoration(
                                color: Colors.white.withOpacity(0.05),
                                borderRadius: BorderRadius.circular(16),
                                border: Border.all(color: Colors.white10),
                              ),
                              child: TextField(
                                controller: _controller,
                                maxLines: null,
                                expands: true,
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 16,
                                ),
                                decoration: const InputDecoration(
                                  hintText:
                                      "Paste your text here to check grammar...",
                                  hintStyle: TextStyle(color: Colors.white30),
                                  border: InputBorder.none,
                                  contentPadding: EdgeInsets.all(20),
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 24),

                    // Result Column
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            "Analysis Result",
                            style: TextStyle(color: Colors.white70),
                          ),
                          const SizedBox(height: 8),
                          Expanded(
                            child: Container(
                              width: double.infinity,
                              decoration: BoxDecoration(
                                color: const Color(
                                  0xFF181825,
                                ), // Slightly darker
                                borderRadius: BorderRadius.circular(16),
                                border: Border.all(color: Colors.white10),
                              ),
                              padding: const EdgeInsets.all(20),
                              child: _isLoading
                                  ? const Center(
                                      child: CircularProgressIndicator(
                                        color: Color(0xFF6C63FF),
                                      ),
                                    )
                                  : SingleChildScrollView(
                                      child: Text(
                                        _result.isEmpty
                                            ? "Results will appear here."
                                            : _result,
                                        style: const TextStyle(
                                          color: Colors.white70,
                                          fontSize: 16,
                                        ),
                                      ),
                                    ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // Action Bar
              Align(
                alignment: Alignment.centerRight,
                child: ElevatedButton.icon(
                  onPressed: _isBackendReady ? _analyzeText : null,
                  icon: const Icon(Icons.auto_fix_high),
                  label: const Text("Check Grammar"),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF6C63FF),
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 24,
                      vertical: 16,
                    ),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    elevation: 4,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
