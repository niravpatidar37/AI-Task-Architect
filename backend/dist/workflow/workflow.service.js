"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
var WorkflowService_1;
Object.defineProperty(exports, "__esModule", { value: true });
exports.WorkflowService = void 0;
const common_1 = require("@nestjs/common");
const config_1 = require("@nestjs/config");
const axios_1 = require("axios");
let WorkflowService = WorkflowService_1 = class WorkflowService {
    constructor(configService) {
        this.configService = configService;
        this.logger = new common_1.Logger(WorkflowService_1.name);
        this.pythonApi = this.configService.get('PYTHON_API_URL') || 'http://localhost:8000';
        this.logger.log(`Using Python AI API at: ${this.pythonApi}`);
    }
    async generateWorkflow(prompt) {
        var _a;
        try {
            const response = await axios_1.default.post(`${this.pythonApi}/generate`, { prompt }, { timeout: 30000 });
            return response.data;
        }
        catch (error) {
            const axiosError = error;
            if (axiosError.response) {
                const statusCode = axiosError.response.status;
                const detail = ((_a = axiosError.response.data) === null || _a === void 0 ? void 0 : _a.detail) || 'AI Engine processing error';
                this.logger.error(`AI Engine failed with ${statusCode}: ${detail}`);
                throw new common_1.HttpException(`Workflow generation failed: ${detail}`, common_1.HttpStatus.INTERNAL_SERVER_ERROR);
            }
            else if (axiosError.code === 'ECONNABORTED' || axiosError.code === 'ECONNREFUSED' || axiosError.code === 'ENOTFOUND') {
                this.logger.error(`Connection error to Python API: ${this.pythonApi}`);
                throw new common_1.HttpException('AI Engine is unavailable or timed out (30s limit). Please check the Python service.', common_1.HttpStatus.SERVICE_UNAVAILABLE);
            }
            else {
                this.logger.error(`Unexpected error during workflow generation: ${axiosError.message}`);
                throw new common_1.HttpException('An unexpected server error occurred.', common_1.HttpStatus.INTERNAL_SERVER_ERROR);
            }
        }
    }
};
exports.WorkflowService = WorkflowService;
exports.WorkflowService = WorkflowService = WorkflowService_1 = __decorate([
    (0, common_1.Injectable)(),
    __metadata("design:paramtypes", [config_1.ConfigService])
], WorkflowService);
//# sourceMappingURL=workflow.service.js.map