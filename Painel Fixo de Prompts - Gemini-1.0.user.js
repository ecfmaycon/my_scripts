// ==UserScript==
// @name         Painel Fixo de Prompts - Gemini
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Painel atualizado com geração de KITs e Auto-Enter
// @author       Você
// @match        https://gemini.google.com/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=google.com
// @run-at       document-idle
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    function criarElemento(tag, estilos = '', texto = '', atributos = {}) {
        const el = document.createElement(tag);
        if (estilos) el.style.cssText = estilos;
        if (texto) el.innerText = texto;
        for (const [chave, valor] of Object.entries(atributos)) {
            el.setAttribute(chave, valor);
        }
        return el;
    }

    function montarPainelFixo() {
        if (document.getElementById('gp-painel-fixo')) return;

        // Container Principal
        const container = criarElemento('div',
            'position:fixed; top:80px; right:20px; width:330px; background:rgba(30, 30, 30, 0.95); border:1px solid #444; border-radius:12px; padding:20px; z-index:999999; box-shadow:0 10px 25px rgba(0,0,0,0.5); font-family:"Segoe UI", sans-serif; color:#fff; backdrop-filter: blur(10px); transition: opacity 0.3s;',
            '', {id: 'gp-painel-fixo'}
        );
        document.body.appendChild(container);

        // Header
        const header = criarElemento('div', 'display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;');
        header.appendChild(criarElemento('h3', 'margin:0; font-size:16px;', '⚡ Gerador de Prompts'));
        const btnMinimizar = criarElemento('button', 'background:none; border:none; color:#aaa; cursor:pointer; font-weight:bold;', '—');
        header.appendChild(btnMinimizar);
        container.appendChild(header);

        // Corpo do Painel
        const corpo = criarElemento('div');
        container.appendChild(corpo);

        // --- CAMPOS DE ENTRADA ---

        // Produto
        const grupoProduto = criarElemento('div');
        grupoProduto.appendChild(criarElemento('label', 'display:block; margin-bottom:5px; font-size:13px; font-weight:bold; color:#ddd;', 'Nome do produto:'));
        const inputProduto = criarElemento('input', 'width:100%; padding:8px; margin-bottom:12px; background:#2d2d2d; border:1px solid #555; color:#fff; border-radius:6px; box-sizing:border-box; font-size:13px;', '', {placeholder: 'Ex: Fone Bluetooth...'});
        grupoProduto.appendChild(inputProduto);
        corpo.appendChild(grupoProduto);

        // Quantidade (NOVO)
        const grupoQuantidade = criarElemento('div', 'display:none;');
        grupoQuantidade.appendChild(criarElemento('label', 'display:block; margin-bottom:5px; font-size:13px; font-weight:bold; color:#ddd;', 'Quantidade de unidades no KIT:'));
        const inputQuantidade = criarElemento('input', 'width:100%; padding:8px; margin-bottom:12px; background:#2d2d2d; border:1px solid #555; color:#fff; border-radius:6px; box-sizing:border-box; font-size:13px;', '', {type: 'number', min: '2', max: '20', value: '2'});
        grupoQuantidade.appendChild(inputQuantidade);
        corpo.appendChild(grupoQuantidade);

        // Especificações
        const grupoSpecs = criarElemento('div', 'display:none;');
        grupoSpecs.appendChild(criarElemento('label', 'display:block; margin-bottom:5px; font-size:13px; font-weight:bold; color:#ddd;', 'Especificações:'));
        const inputSpecs = criarElemento('textarea', 'width:100%; padding:8px; margin-bottom:12px; background:#2d2d2d; border:1px solid #555; color:#fff; border-radius:6px; box-sizing:border-box; resize:none; font-size:13px;', '', {rows: '3', placeholder: 'Detalhes...'});
        grupoSpecs.appendChild(inputSpecs);
        corpo.appendChild(grupoSpecs);

        // --- OPÇÕES (RÁDIOS) ---
        corpo.appendChild(criarElemento('label', 'display:block; margin-bottom:8px; font-size:13px; font-weight:bold; color:#ddd;', 'Estilo da imagem:'));
        const grupoRadios = criarElemento('div', 'margin-bottom:15px; font-size:12px; line-height:1.5;');

        const radios = [];
        const opcoes = [
            {val: '1', texto: ' 1. Apenas produto (Fundo contextual)'},
            {val: '2', texto: ' 2. Pessoa utilizando o produto'},
            {val: '3', texto: ' 3. Foto de benefícios c/ especificações'},
            {val: '4', texto: ' 4. Gráfico Comparação (Produto + Specs)'},
            {val: '5', texto: ' 5. Criar imagem de KIT ambientado'} // NOVA OPÇÃO
        ];

        opcoes.forEach((op, index) => {
            const label = criarElemento('label', 'display:block; margin-bottom:6px; cursor:pointer;');
            const radio = criarElemento('input', '', '', {type: 'radio', name: 'gptipo', value: op.val});
            if(index === 0) radio.checked = true;
            radios.push(radio);
            label.appendChild(radio);
            label.appendChild(document.createTextNode(op.texto));
            grupoRadios.appendChild(label);
        });
        corpo.appendChild(grupoRadios);

        // --- BOTÃO GERAR ---
        const btnGerar = criarElemento('button', 'width:100%; padding:10px; background:#0b57d0; color:white; border:none; border-radius:6px; cursor:pointer; font-weight:bold; font-size:14px;', 'Gerar e Enviar 🚀');
        corpo.appendChild(btnGerar);

        // --- LÓGICA DE EVENTOS ---

        // Minimizar
        let minimizado = false;
        btnMinimizar.addEventListener('click', () => {
            minimizado = !minimizado;
            corpo.style.display = minimizado ? 'none' : 'block';
            btnMinimizar.innerText = minimizado ? '▼' : '—';
            container.style.width = minimizado ? 'auto' : '330px';
        });

        // Controle de Visibilidade
        radios.forEach(radio => {
            radio.addEventListener('change', (e) => {
                const val = e.target.value;
                // Exibe Produto para opções 1, 2, 4 e 5
                grupoProduto.style.display = (val === '1' || val === '2' || val === '4' || val === '5') ? 'block' : 'none';
                // Exibe Specs para opções 3 e 4
                grupoSpecs.style.display = (val === '3' || val === '4') ? 'block' : 'none';
                // Exibe Quantidade apenas para opção 5
                grupoQuantidade.style.display = (val === '5') ? 'block' : 'none';
            });
        });

        btnGerar.addEventListener('mouseover', () => btnGerar.style.background = '#0842a0');
        btnGerar.addEventListener('mouseout', () => btnGerar.style.background = '#0b57d0');

        // Geração do Prompt
        btnGerar.addEventListener('click', () => {
            const produto = inputProduto.value.trim();
            const specs = inputSpecs.value.trim();
            let quantidade = parseInt(inputQuantidade.value);
            const tipo = radios.find(r => r.checked).value;

            let promptText = "";

            // Validações
            if ((tipo === '1' || tipo === '2' || tipo === '5') && !produto) return alert("⚠️ Digite o nome do produto.");
            if (tipo === '3' && !specs) return alert("⚠️ Digite as especificações.");
            if (tipo === '4' && (!produto || !specs)) return alert("⚠️ Preencha Produto e Especificações.");

            // Corrige se a quantidade for menor que 2 na opção 5
            if (tipo === '5' && (isNaN(quantidade) || quantidade < 2)) {
                quantidade = 2;
                inputQuantidade.value = 2;
            }

            // Construção dos textos conforme AHK v3
            if (tipo === '1') {
                promptText = `Gere 1 única imagem realista de alta qualidade para uso em anúncio de e-commerce (Mercado Livre). O foco principal deve ser ${produto}, mantendo 100% fidelidade ao design original do produto, sem alterações de cor, formato, proporção ou detalhes. O produto deve estar em destaque central, bem iluminado, com aparência profissional de fotografia comercial. Crie um ambiente contextual realista ao redor do produto, adequado ao seu uso (ex: cozinha moderna, escritório, sala, etc.), transmitindo valor e credibilidade. Utilize iluminação natural ou de estúdio suave, com sombras realistas e fundo limpo, evitando poluição visual. A composição deve parecer uma foto publicitária premium, com foco nítido no produto e leve desfoque no fundo (efeito depth of field). Alta resolução, estilo fotográfico realista.`;
            } else if (tipo === '2') {
                promptText = `Gere 1 única imagem realista de alta qualidade para e-commerce, mostrando uma pessoa utilizando o ${produto} de forma natural em um ambiente cotidiano. O produto deve manter 100% fidelidade ao original, sem qualquer alteração de cor, formato, textura ou proporções. A cena deve transmitir conforto e uso real, com a pessoa em postura natural, em um ambiente coerente e bem organizado. Utilize iluminação suave e realista, com aparência de fotografia profissional, mantendo o produto como elemento principal e bem destacado na composição.`;
            } else if (tipo === '3') {
                promptText = `crie uma foto mostrando os benefícios detalhados com estas informações: \n${specs}`;
            } else if (tipo === '4') {
                promptText = `Gere um gráfico de comparação de marketing profissional e de alta resolução. A composição e o estilo devem corresponder à estrutura, layout, tipografia e esquema de cores da imagem anexada (image_0.png), usando tipografia limpa e sem serifa.\n\n**Layout Geral e Cores:**\nO gráfico é dividido em dois painéis verticais distintos com cantos arredondados. O fundo é dividido horizontalmente: a seção superior é um marrom-avermelhado profundo e rico com detalhes em linhas curvas claras no canto superior direito. A seção inferior é branca e limpa.\n\n**Cabeçalhos Superiores:**\n- Cabeçalho Esquerdo: '${produto}' em uma fonte branca e limpa.\n- Cabeçalho Direito: 'Marcas Simples' em uma fonte branca e limpa.\n\n**Painéis Centrais de Exibição de Imagens:**\n- **Painel de Imagem Esquerdo (Nosso Produto):** Crie uma renderização de produto limpa e fotorrealista de uma versão premium do ${produto}. Ele deve ser colocado em um ambiente doméstico ou comercial sofisticado e bem iluminado.\n- **Painel de Imagem Direito (Alternativa Inferior):** Crie uma renderização de produto limpa e fotorrealista de uma versão genérica e inferior do mesmo tipo de produto. Coloque-o em um ambiente mais simples com iluminação mais plana.\n\n**Listas de Benefícios Inferiores:**\nAbaixo das imagens, crie duas listas verticais paralelas e limpas com ícones. Use estritamente as especificações abaixo para montar os tópicos:\n\n[ESPECIFICAÇÕES]:\n${specs}\n\n- **Lista Esquerda (Nossos Benefícios):** Precedida por ícones de 'check' verdes. Gere pontos positivos baseados exclusivamente nas [ESPECIFICAÇÕES].\n- **Lista Direita (Pontos Inferiores):** Precedida por ícones de 'X' vermelhos. Gere pontos negativos correspondentes.\n\n**Detalhes Finais:**\nGaranta que a hierarquia visual e o espaçamento sejam idênticos à image_0.png. Texto legível e perfeitamente alinhado.`;
            } else if (tipo === '5') {
                promptText = `Gere 1 única imagem fotográfica realista de alta qualidade para anúncio de e-commerce, apresentando um KIT contendo exatamente ${quantidade} unidades idênticas do produto: ${produto}. As unidades devem manter 100% de fidelidade ao design, cor e proporções originais. A composição deve mostrar as ${quantidade} unidades dispostas de forma organizada e esteticamente agradável dentro de um ambiente contextual realista e sofisticado, adequado ao uso do produto (ex: uma sala de estar, uma cozinha, um banheiro, etc.). O cenário e o ângulo da câmera devem ser ajustados e ampliados para acomodar todas as unidades de forma natural, sem parecerem espremidas. Utilize iluminação profissional de estúdio que valorize as texturas dos produtos, com sombras realistas que conectem os objetos ao cenário. O foco deve ser nítido em todo o kit, com o fundo do ambiente levemente desfocado. Alta resolução, aparência de fotografia publicitária premium.`;
            }

            // Injeção e Auto-Enter
            const chatInputBox = document.querySelector('rich-textarea p, .ql-editor p, div[contenteditable="true"]');

            if (chatInputBox) {
                chatInputBox.focus();
                document.execCommand('insertText', false, promptText);

                // Feedback
                btnGerar.innerText = "Enviando... 🚀";
                btnGerar.style.background = "#0f9d58";

                setTimeout(() => {
                    const btnEnviar = document.querySelector('button[aria-label*="Send"], button[aria-label*="Enviar"], button[mattooltip*="Send"], button[mattooltip*="Enviar"]');

                    if (btnEnviar && !btnEnviar.disabled) {
                        btnEnviar.click();
                    } else {
                        const enterEvent = new KeyboardEvent('keydown', { bubbles: true, cancelable: true, key: 'Enter', code: 'Enter', keyCode: 13 });
                        chatInputBox.dispatchEvent(enterEvent);
                    }

                    setTimeout(() => {
                        btnGerar.innerText = "Gerar e Enviar 🚀";
                        btnGerar.style.background = "#0b57d0";
                    }, 1500);

                }, 200);

            } else {
                navigator.clipboard.writeText(promptText);
                alert("✅ Prompt copiado! O Google escondeu a caixa de texto, dê Ctrl+V e Enter.");
            }
        });
    }

    const observer = setInterval(() => {
        if (document.body) {
            montarPainelFixo();
            clearInterval(observer);
        }
    }, 1000);

})();