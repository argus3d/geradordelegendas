# Gerador de Legendas — IESDE

Aplicativo desktop para gerar legendas `.srt` a partir de vídeos MP4 usando modelos Whisper. A interface foi desenvolvida em Python com Tkinter, com opção de processamento pela CPU ou por GPU NVIDIA compatível com CUDA.

## Recursos

- Geração automática de legendas em português.
- Seleção de um único vídeo `.mp4` ou de uma pasta com vários vídeos.
- Opções de modelo Whisper: `tiny`, `base`, `small`, `medium` e `large`.
- Seleção de processamento por CPU ou GPU CUDA, quando disponível.
- Criação do arquivo `.srt` na mesma pasta do vídeo, usando o mesmo nome-base.
- Interface gráfica com registro de progresso e mensagens de erro.
- Uso de FFmpeg incluído junto ao aplicativo.

## Requisitos

- Windows.
- Python 3.12 recomendado para desenvolvimento/compilação.
- Dependências Python:
  - `torch`
  - `stable-ts` (disponibiliza o módulo `stable_whisper`)
  - `tkinter` (normalmente incluído na instalação do Python para Windows)
- FFmpeg para leitura/processamento dos arquivos de vídeo.
- Para usar GPU: placa NVIDIA, driver compatível e instalação do PyTorch com suporte CUDA compatível com o ambiente.

> A primeira utilização de cada modelo pode exigir o download dos pesos do Whisper. O modelo `large` tende a consumir mais memória e tempo de processamento do que os modelos menores.

## Instalação para desenvolvimento

1. Instale o Python para Windows.
2. Abra o CMD na pasta do projeto.
3. Instale as dependências:

```bat
python -m pip install --upgrade pip
python -m pip install torch stable-ts pyinstaller
```

4. Coloque o FFmpeg no projeto com esta estrutura:

```text
projeto/
├── legenda_v2.py
└── ffmpeg/
    └── ffmpeg.exe
```

5. Execute o aplicativo:

```bat
python legenda_v2.py
```

Se o PyTorch instalado não tiver suporte CUDA, a opção de GPU não estará disponível e o processamento deverá ser feito pela CPU.

## Gerar o executável EXE

Abra o CMD na pasta do projeto e execute:

```bat
pyinstaller --noconfirm --onedir --add-binary "ffmpeg\ffmpeg.exe;ffmpeg" legenda_v2.py
```

O executável e os arquivos distribuídos serão criados na pasta `dist`. A opção `--onedir` gera uma pasta com o executável e seus arquivos de suporte; não é um EXE totalmente independente em um único arquivo.

### Conferir a estrutura da pasta `dist`

O programa procura o FFmpeg em uma pasta chamada `ffmpeg`, ao lado do script ou do executável. Portanto, mantenha a estrutura assim:

```text
dist/
└── legenda_v2/
    ├── legenda_v2.exe
    ├── ffmpeg/
    │   └── ffmpeg.exe
    └── _internal/
        └── ... arquivos e dependências do aplicativo ...
```

O nome da pasta de saída pode variar conforme a configuração do PyInstaller.

### Pasta `whisper`

Se a compilação não incluir corretamente os arquivos do pacote Whisper, a orientação usada neste projeto é copiar a pasta `whisper` instalada no Python para dentro de `_internal`, por exemplo a partir de:

```text
C:\Users\<SEU_USUARIO>\AppData\Local\Programs\Python\Python312\Lib\site-packages\whisper
```

Copie a pasta `whisper` inteira para `dist\legenda_v2\_internal\whisper`. O caminho acima é apenas um exemplo: substitua `<SEU_USUARIO>` pelo nome da pasta do usuário do Windows onde o Python está instalado.

Copie também a pasta `ffmpeg` para a pasta de saída do aplicativo, no mesmo nível de `legenda_v2.exe`, se ela ainda não tiver sido incluída pela compilação. O arquivo deve ficar em `ffmpeg\ffmpeg.exe`.

> Depois de copiar os arquivos, teste o executável em um computador diferente daquele usado para compilar. A presença dos arquivos não garante, por si só, que todas as dependências do PyTorch/CUDA estejam disponíveis nesse computador.

## Como usar

1. Abra `legenda_v2.exe`.
2. Escolha **Um arquivo** para selecionar um vídeo MP4 ou **Uma pasta** para processar os arquivos MP4 que estão diretamente naquela pasta.
3. Escolha o dispositivo: **CPU** ou **GPU (CUDA)**.
4. Escolha o modelo Whisper.
5. Clique em **Gerar Legendas**.
6. Aguarde a conclusão. O arquivo `.srt` será salvo ao lado do vídeo original.

Ao selecionar uma pasta, o aplicativo procura arquivos `.mp4` diretamente nela; subpastas não são percorridas recursivamente.

## Modelos Whisper

| Modelo | Característica geral |
|---|---|
| `tiny` | Mais rápido e leve; pode ter menor precisão. |
| `base` | Leve, com precisão geralmente superior à do `tiny`. |
| `small` | Equilíbrio entre velocidade e precisão. |
| `medium` | Maior custo de processamento e, em geral, melhor reconhecimento. |
| `large` | Maior exigência de memória e processamento; pode oferecer melhor precisão, dependendo do áudio. |

A velocidade e a precisão variam conforme o idioma, a qualidade do áudio, o hardware e o modelo utilizado.

## Solução de problemas

**Erro: `ffmpeg.exe não encontrado`**
- Confira se o arquivo existe em `ffmpeg\ffmpeg.exe`.
- No pacote compilado, a pasta `ffmpeg` deve estar ao lado do executável.
- Recompile usando o comando de PyInstaller apresentado acima, se necessário.

**Erro ao selecionar GPU CUDA**
- Confirme se o driver NVIDIA está instalado e atualizado.
- Verifique se a versão do PyTorch instalada oferece suporte CUDA compatível.
- Se a GPU não estiver disponível, selecione CPU.

**O aplicativo funciona no computador de desenvolvimento, mas não em outro**
- Confira se a pasta `_internal` está completa.
- Confira se `whisper` está dentro de `_internal`, caso seja necessário copiá-la manualmente.
- Confira se `ffmpeg\ffmpeg.exe` está junto ao executável.
- Teste primeiro com CPU para ajudar a distinguir problemas de dependência CUDA de problemas gerais do aplicativo.

**O modelo demora para carregar**
- O carregamento inicial pode demorar, especialmente com `medium` e `large`.
- Esses modelos também podem exigir mais memória RAM ou VRAM.

## Tecnologias

- Python
- Tkinter
- PyTorch
- Stable-ts / Whisper
- FFmpeg
- PyInstaller

## Observações

- O aplicativo está configurado para transcrever em português (`language="pt"`).
- O código remove segmentos identificados como `Music` ou `Música` antes de exportar as legendas. Isso não garante a remoção de toda música ou de todos os sons sem fala.
- Os arquivos `.srt` existentes com o mesmo nome-base podem ser sobrescritos.
- Verifique as licenças e condições de distribuição das dependências e dos modelos antes de redistribuir o aplicativo.

## Licença

Defina aqui a licença do projeto antes de publicá-lo publicamente no GitHub.
