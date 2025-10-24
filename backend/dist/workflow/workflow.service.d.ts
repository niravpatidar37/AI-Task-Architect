import { ConfigService } from '@nestjs/config';
export declare class WorkflowService {
    private readonly configService;
    private readonly logger;
    private readonly pythonApi;
    constructor(configService: ConfigService);
    generateWorkflow(prompt: string): Promise<any>;
}
