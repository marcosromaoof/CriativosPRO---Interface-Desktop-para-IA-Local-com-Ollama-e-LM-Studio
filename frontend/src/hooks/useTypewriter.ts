import { useState, useEffect, useRef } from 'react';

/**
 * Hook para efeito de máquina de escrever (Typewriter).
 * Suaviza a renderização de texto recebido via stream.
 * 
 * @param text O texto completo atual (que cresce com o tempo).
 * @param speed Velocidade base em ms (padrão 10ms).
 * @param enabled Se o efeito deve ser ativo (útil para desativar em histórico antigo).
 */
export function useTypewriter(text: string, speed: number = 10, enabled: boolean = true) {
    const [displayedText, setDisplayedText] = useState('');
    const index = useRef(0);

    useEffect(() => {
        // Reset imediato se desabilitado ou se o texto mudou drasticamente (novo chat)
        // Comparar se o text atual começa com o que já mostramos ajuda a não resetar em streaming
        if (!enabled) {
            setDisplayedText(text);
            index.current = text.length;
            return;
        }

        // Se o texto alvo é menor que o atual (ex: retry), reseta
        if (text.length < index.current) {
            index.current = 0;
            setDisplayedText('');
        }
    }, [enabled, text]); // Monitora mudanças "macro"

    useEffect(() => {
        if (!enabled) return;

        // Se ainda há o que digitar
        if (index.current < text.length) {
            const bufferSize = text.length - index.current;
            let charsPerTick = 1;
            let currentSpeed = speed;

            if (bufferSize > 150) {
                charsPerTick = 25;
                currentSpeed = 1;
            } else if (bufferSize > 80) {
                charsPerTick = 12;
                currentSpeed = 1;
            } else if (bufferSize > 30) {
                charsPerTick = 6;
                currentSpeed = 1;
            } else if (bufferSize > 10) {
                charsPerTick = 3;
                currentSpeed = 5;
            } else {
                charsPerTick = 1;
                currentSpeed = 15;
            }

            const timeoutId = setTimeout(() => {
                // Incrementa múltiplos caracteres se necessário
                index.current = Math.min(index.current + charsPerTick, text.length);
                setDisplayedText(text.slice(0, index.current));
            }, currentSpeed);

            return () => clearTimeout(timeoutId);
        }
    }, [text, enabled, speed, displayedText]);
    // Mantemos displayedText na dependência para criar o loop do efeito
    // (A cada render que atualiza o texto, o effect roda de novo para o próximo char)

    return displayedText;
}
