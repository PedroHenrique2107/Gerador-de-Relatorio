/**
 * tailwind.config.js
 *
 * Arquivo de configuraÃ§Ã£o do TailwindCSS.
 * Aqui definimos:
 * - Onde o Tailwind deve procurar classes (content)
 * - Tema customizado (cores, radius, animaÃ§Ãµes)
 * - Plugins adicionais
 *
 * âš ï¸ Se for fazer manutenÃ§Ã£o no futuro:
 * - AlteraÃ§Ãµes visuais globais (cores, radius, animaÃ§Ãµes) devem ser feitas aqui.
 * - Evite colocar valores fixos nos componentes se jÃ¡ existir variÃ¡vel aqui.
 */

/** @type {import('tailwindcss').Config} */
module.exports = {
  /**
   * Habilita modo escuro baseado em classe.
   * Para ativar dark mode:
   * <html class="dark">
   */
  darkMode: ["class"],

  /**
   * Arquivos onde o Tailwind vai procurar classes.
   * Se criar novas pastas (ex: components, layouts),
   * adicione aqui para nÃ£o quebrar o purge.
   */
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],

  theme: {
    extend: {

      /**
       * Border radius customizado usando variÃ¡vel CSS (--radius).
       * Permite mudar o arredondamento global apenas alterando a variÃ¡vel.
       */
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)'
      },

      /**
       * Sistema de cores baseado em variÃ¡veis CSS (HSL).
       * Isso permite:
       * - Troca dinÃ¢mica de tema (light/dark)
       * - FÃ¡cil manutenÃ§Ã£o futura
       *
       * âš ï¸ As variÃ¡veis (--background, --primary, etc.)
       * devem existir no CSS global (ex: index.css).
       */
      colors: {
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',

        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))'
        },

        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))'
        },

        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))'
        },

        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))'
        },

        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))'
        },

        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))'
        },

        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))'
        },

        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',

        /**
         * Cores especÃ­ficas para grÃ¡ficos.
         * Pode ser usado com bibliotecas de chart.
         */
        chart: {
          '1': 'hsl(var(--chart-1))',
          '2': 'hsl(var(--chart-2))',
          '3': 'hsl(var(--chart-3))',
          '4': 'hsl(var(--chart-4))',
          '5': 'hsl(var(--chart-5))'
        }
      },

      /**
       * AnimaÃ§Ãµes personalizadas (usadas normalmente com Radix UI Accordion).
       * Controlam abertura e fechamento suave.
       */
      keyframes: {
        'accordion-down': {
          from: { height: '0' },
          to: { height: 'var(--radix-accordion-content-height)' }
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: '0' }
        }
      },

      /**
       * Define como as animaÃ§Ãµes serÃ£o usadas.
       * DuraÃ§Ã£o: 0.2s
       * Easing: ease-out
       */
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out'
      }
    }
  },

  /**
   * Plugins extras do Tailwind.
   * tailwindcss-animate adiciona utilitÃ¡rios de animaÃ§Ã£o.
   *
   * âš ï¸ Se remover esse plugin, animaÃ§Ãµes podem parar de funcionar.
   */
  plugins: [require("tailwindcss-animate")],
};
