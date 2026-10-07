import 'package:flutter/material.dart';
import 'package:google_generative_ai/google_generative_ai.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';


class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  _ChatScreenState createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _controller = TextEditingController();
  final List<ChatMessage> _messages = [];
  final ScrollController _scrollController = ScrollController();
  bool _isTyping = false;
  late GenerativeModel model;
  late ChatSession chat;

  // Modifica la inicialización del chat en initState()
  @override
  void initState() {
    super.initState();
    final apiKey = dotenv.env['GEMINI_API_KEY'] ?? '';
    model = GenerativeModel(
      model: 'gemini-pro',
      apiKey: apiKey,
    );
    chat = model.startChat(
      history: [
        Content.text(
          '''Eres un asistente virtual de la Universidad. Solo respondes preguntas relacionadas con:
          - Horarios de clases y servicios
          - Ubicaciones dentro del campus
          - Trámites y procedimientos universitarios
          - Información sobre carreras y facultades
          - Eventos universitarios
          - Servicios estudiantiles (biblioteca, casino, deportes, etc.)
          - Informacion sobre asignaturas (evaluaciones, contenidos, etc.)
          
          Si te preguntan algo no relacionado con la universidad, responde: "Lo siento, solo puedo ayudarte con temas relacionados con la Universidad."
          
          Mantén tus respuestas concisas y relevantes para los estudiantes.
          
          Considera la siguiente informacion de la asignatura de ---   
        '''
        ),
      ],
    );
  }
      
 
  Future<void> _sendMessage(String message) async {
    if (message.trim().isEmpty) return;

    setState(() {
      _messages.add(ChatMessage(text: message, isUser: true));
      _isTyping = true;
    });
    
    _controller.clear();
    _scrollToBottom();

    try {
      final response = await chat.sendMessage(Content.text(message));
      final botResponse = response.text ?? 'No pude generar una respuesta';
      
      setState(() {
        _messages.add(ChatMessage(text: botResponse, isUser: false));
        _isTyping = false;
      });
      
      _scrollToBottom();
    } catch (e) {
      setState(() {
        _messages.add(
          ChatMessage(
            text: 'Error al enviar el mensaje. Por favor intenta nuevamente.',
            isUser: false,
          ),
        );
        _isTyping = false;
      });
    }
  }

  void _scrollToBottom() {
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Asistente UDEC',
          style: TextStyle(
            fontFamily: 'Jost',
            color: Colors.black,
          ),
        ),
        backgroundColor: const Color(0xFFD9E6FF),
        iconTheme: const IconThemeData(color: Colors.black),
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(8.0),
              itemCount: _messages.length,
              itemBuilder: (context, index) => _messages[index],
            ),
          ),
          if (_isTyping)
            const Padding(
              padding: EdgeInsets.all(8.0),
              child: CircularProgressIndicator(),
            ),
          Container(
            decoration: BoxDecoration(
              color: Colors.white,
              border: Border(top: BorderSide(color: Colors.grey[300]!)),
            ),
            child: _buildTextComposer(),
          ),
        ],
      ),
    );
  }

  Widget _buildTextComposer() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 8.0),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _controller,
              decoration: InputDecoration(
                hintText: 'Escribe un mensaje...',
                filled: true,
                fillColor: Colors.grey[100],
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(20.0),
                  borderSide: BorderSide.none,
                ),
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 16.0,
                  vertical: 8.0,
                ),
              ),
              onSubmitted: _isTyping ? null : _sendMessage,
            ),
          ),
          const SizedBox(width: 8.0),
          Container(
            decoration: BoxDecoration(
              color: const Color(0xFFD9E6FF),
              borderRadius: BorderRadius.circular(20.0),
            ),
            child: IconButton(
              icon: const Icon(Icons.send),
              onPressed: _isTyping ? null : () => _sendMessage(_controller.text),
              color: Colors.black,
            ),
          ),
        ],
      ),
    );
  }
}

class ChatMessage extends StatelessWidget {
  final String text;
  final bool isUser;

  const ChatMessage({
    super.key,
    required this.text,
    required this.isUser,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        mainAxisAlignment:
            isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        children: [
          Flexible(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 10.0),
              margin: EdgeInsets.only(
                left: isUser ? 64.0 : 8.0,
                right: isUser ? 8.0 : 64.0,
              ),
              decoration: BoxDecoration(
                color: isUser ? const Color(0xFFD9E6FF) : Colors.grey[200],
                borderRadius: BorderRadius.circular(20.0),
              ),
              child: Text(
                text,
                style: const TextStyle(
                  fontFamily: 'Jost',
                  color: Colors.black,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}