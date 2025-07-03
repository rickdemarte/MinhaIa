Claro, vou te fornecer um passo a passo simples para configurar o VSCode com seu usuário e sincronizar seu projeto no GitHub.com. Siga estas etapas:

1. **Configurar o usuário no VSCode**:
   - Abra o VSCode.
   - Clique no ícone de usuário no canto inferior esquerdo da janela.
   - Selecione "Entrar" e faça login com sua conta do GitHub.
   - Após o login, você verá seu nome de usuário do GitHub exibido no canto inferior esquerdo.

2. **Criar um novo repositório no GitHub.com**:
   - Acesse o site do GitHub.com e faça login com sua conta.
   - Clique no ícone "+" no canto superior direito e selecione "Novo repositório".
   - Digite um nome para o seu repositório e adicione uma descrição (opcional).
   - Decida se você deseja que o repositório seja público ou privado.
   - Selecione "Criar repositório".

3. **Inicializar um novo projeto no VSCode e conectá-lo ao GitHub**:
   - No VSCode, crie um novo diretório para seu projeto.
   - Abra esse diretório no VSCode.
   - Abra o terminal integrado do VSCode (Ctrl+Shift+`) ou vá em Terminal > Novo Terminal.
   - No terminal, execute o seguinte comando para inicializar um novo repositório Git:
     ```
     git init
     ```
   - Agora, execute o seguinte comando para conectar seu repositório local ao repositório remoto no GitHub:
     ```
     git remote add origin https://github.com/seu-usuario/seu-repositorio.git
     ```
     Substitua `seu-usuario` e `seu-repositorio` pelos valores correspondentes.

4. **Adicionar, commitar e enviar seu projeto para o GitHub**:
   - No terminal do VSCode, execute o seguinte comando para adicionar todos os arquivos do seu projeto ao Git:
     ```
     git add .
     ```
   - Em seguida, execute o seguinte comando para fazer um commit das alterações:
     ```
     git commit -m "Commit inicial"
     ```
   - Finalmente, execute o seguinte comando para enviar seu projeto para o repositório remoto no GitHub:
     ```
     git push -u origin master
     ```
   - Após concluir essa etapa, seu projeto estará sincronizado com o GitHub.

Agora, sempre que você fizer alterações em seu projeto, basta repetir os passos 4 (adicionar, commitar e enviar) para manter seu repositório remoto no GitHub atualizado.

Lembre-se de que você pode adicionar mais funcionalidades e configurações avançadas ao seu ambiente de desenvolvimento no VSCode, como a instalação de extensões, configuração de atalhos, etc. Mas esse passo a passo básico deve ser suficiente para você começar a trabalhar com o VSCode e o GitHub.